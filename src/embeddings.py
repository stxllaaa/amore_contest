"""
벡터 스토어 구축 및 관리
products, reviews, brand_tone 데이터 임베딩
"""

import os
import pandas as pd
from pathlib import Path
from typing import List, Dict
import pickle

from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_community.vectorstores import FAISS
from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter


class VectorStoreManager:
    """벡터 스토어 관리 클래스"""

    def __init__(self, db_path: str = "./brands_db", vector_path: str = "./vector_store"):
        self.db_path = Path(db_path)
        self.vector_path = Path(vector_path)
        self.vector_path.mkdir(exist_ok=True)

        # Google Gemini Embeddings
        self.embeddings = GoogleGenerativeAIEmbeddings(
            model=os.getenv("EMBEDDING_MODEL", "models/text-embedding-004"),
            google_api_key=os.getenv("GOOGLE_API_KEY")
        )

        self.products_store = None
        self.tone_store = None
        self.reviews_store = None
        self.ingredients_store = None

    def build_all_stores(self):
        """모든 벡터 스토어 구축"""
        print("[Vector Store] 벡터 스토어 구축 시작...")

        self.products_store = self._build_products_store()
        self.tone_store = self._build_tone_store()
        self.reviews_store = self._build_reviews_store()
        self.ingredients_store = self._build_ingredients_store()

        self._save_stores()
        print("[Vector Store] 모든 벡터 스토어 구축 완료!")

    def _build_products_store(self) -> FAISS:
        """제품 데이터 벡터 스토어 구축 (통합 CSV 사용)"""
        print("  - 제품 데이터 임베딩 중...")
        documents = []

        # 통합 products CSV 파일 읽기
        products_file = self.db_path / "products_db" / "all_products.csv"
        df = pd.read_csv(products_file, encoding='utf-8-sig')

        for _, row in df.iterrows():
            # 가격 파싱 (쉼표 제거)
            price_str = str(row['price']).replace(',', '').strip()
            try:
                price = int(price_str)
            except:
                price = 0

            # 제품 정보를 텍스트로 변환
            text = f"""
            제품명: {row['product_name']}
            브랜드: {row['brand']}
            카테고리: {row['category']}
            주성분: {row.get('main_ingredients', 'N/A')}
            가격: {price:,}원
            긍정 키워드: {row.get('good', 'N/A')}
            부정 키워드: {row.get('bad', 'N/A')}
            """.strip()

            metadata = {
                "product_id": row['product_id'],
                "product_name": row['product_name'],
                "brand": row['brand'],
                "category": row['category'],
                "price": price,
                "good_keywords": str(row.get('good', '')),
                "bad_keywords": str(row.get('bad', ''))
            }

            documents.append(Document(page_content=text, metadata=metadata))

        return FAISS.from_documents(documents, self.embeddings)

    def _build_tone_store(self) -> FAISS:
        """브랜드 톤 코퍼스 벡터 스토어 구축

        시스템은 `marketing_tone_info.csv`를 우선 사용합니다. CSV가 없고
        `marketing_tone_info.xlsx`가 존재하면 자동으로 CSV로 변환 후 사용합니다.
        (과거의 per-brand CSV 파일은 더 이상 기본 사용 대상이 아닙니다.)
        """
        print("  - 브랜드 톤 데이터 임베딩 중...")
        documents = []

        tone_dir = self.db_path / "brand_tone_corpus"
        csv_file = tone_dir / "marketing_tone_info.csv"
        xlsx_file = tone_dir / "marketing_tone_info.xlsx"

        df = None
        if csv_file.exists():
            print(f"    - marketing_tone_info.csv 로드: {csv_file}")
            df = pd.read_csv(csv_file, encoding='utf-8-sig')
        elif xlsx_file.exists():
            print(f"    - marketing_tone_info.xlsx 로드: {xlsx_file} (CSV로 변환합니다)")
            df = pd.read_excel(xlsx_file)
            try:
                df.to_csv(csv_file, index=False, encoding='utf-8-sig')
                print(f"    - 변환 완료: {csv_file}")
            except Exception as e:
                print(f"    ⚠ CSV 변환 실패: {e}")
        else:
            # Fallback: deprecated per-brand *_tone_texts.csv 탐색
            print("    ⚠ 브랜드 톤 파일이 없습니다. per-brand *_tone_texts.csv를 탐색합니다 (권장: marketing_tone_info.csv 사용)")
            tone_files = list(tone_dir.glob("*_tone_texts.csv"))
            if tone_files:
                dfs = []
                for f in tone_files:
                    try:
                        d = pd.read_csv(f, encoding='utf-8-sig')
                        # 표준 컬럼으로 정제
                        if 'tone_text' not in d.columns:
                            # 첫 번째 컬럼을 tone_text로 간주
                            d = d.rename(columns={d.columns[0]: 'tone_text'})
                        if 'brand' not in d.columns:
                            brand_from = f.stem.split('_')[0]
                            d['brand'] = brand_from
                        # platform 컬럼이 없으면 공백으로 채움
                        if 'platform' not in d.columns:
                            d['platform'] = ''
                        dfs.append(d[['brand', 'platform', 'tone_text']])
                    except Exception as e:
                        print(f"      ⚠ {f} 읽기 실패: {e}")
                if dfs:
                    df = pd.concat(dfs, ignore_index=True)

        if df is None or df.empty:
            print("    ⚠ 브랜드 톤 데이터가 없어 빈 스토어를 생성합니다.")
            dummy = Document(page_content="No tone data", metadata={"brand": "dummy", "platform": "none"})
            return FAISS.from_documents([dummy], self.embeddings)

        for _, row in df.iterrows():
            metadata = {
                "brand": row.get('brand', ''),
                "platform": row.get('platform', '')
            }
            text = str(row.get('tone_text', ''))
            documents.append(Document(page_content=text, metadata=metadata))

        return FAISS.from_documents(documents, self.embeddings)

    def _build_reviews_store(self) -> FAISS:
        """리뷰 데이터 벡터 스토어 구축 (통합 CSV 사용)"""
        print("  - 리뷰 데이터 임베딩 중...")
        documents = []

        # 통합 reviews CSV 파일 읽기
        reviews_file = self.db_path / "reviews_db" / "all_reviews.csv"
        df = pd.read_csv(reviews_file, encoding='utf-8-sig')

        # lifestyle 컬럼 파싱 (문자열 리스트 형식)
        for _, row in df.iterrows():
            lifestyle_str = str(row.get('lifestyle', ''))

            # 빈 값이나 "[]" 형태는 스킵
            if not lifestyle_str or lifestyle_str == '[]' or lifestyle_str.lower() == 'nan':
                continue

            # 리뷰 텍스트에 라이프스타일 컨텍스트 추가
            enriched_text = f"{row['review_text']} [라이프스타일: {lifestyle_str}]"

            metadata = {
                "product_id": row['product_id'],
                "brand": row['brand'],
                "age_group": row.get('age_group', ''),
                "gender": row.get('gender', ''),
                "skin_type": row.get('skin_type', ''),
                "skin_concerns": row.get('skin_concerns', ''),
                "category": row.get('category', ''),
                "good_keywords": str(row.get('good', '')),
                "bad_keywords": str(row.get('bad', '')),
                "lifestyle": lifestyle_str
            }

            documents.append(
                Document(page_content=enriched_text, metadata=metadata)
            )

        print(f"    총 {len(documents)}개의 리뷰 임베딩")
        return FAISS.from_documents(documents, self.embeddings)

    def _build_ingredients_store(self) -> FAISS:
        """성분 데이터 벡터 스토어 구축"""
        print("  - 성분 데이터 임베딩 중...")
        documents = []

        # 성분 CSV 파일 읽기
        ingredients_file = Path("ingredients_db") / "cosmetic_ingredients.csv"

        # 파일이 없으면 빈 스토어 생성
        if not ingredients_file.exists():
            print("    ⚠ 성분 DB 파일이 없습니다. 빈 벡터 스토어 생성")
            # 더미 문서로 빈 벡터 스토어 생성
            dummy_doc = Document(
                page_content="No ingredients data",
                metadata={"ingredient_id": "dummy"}
            )
            return FAISS.from_documents([dummy_doc], self.embeddings)

        df = pd.read_csv(ingredients_file, encoding='utf-8-sig')

        for _, row in df.iterrows():
            # 성분 정보를 텍스트로 변환
            text = f"""
            성분명(한글): {row['ingredient_kor']}
            성분명(영문): {row['ingredient_eng']}
            효능: {row['function']}
            설명: {row['description']}
            피부 고민: {row['skin_concerns']}
            """.strip()

            metadata = {
                "ingredient_id": row['ingredient_id'],
                "ingredient_eng": row['ingredient_eng'],
                "ingredient_kor": row['ingredient_kor'],
                "function": str(row['function']),
                "description": str(row['description']),
                "skin_concerns": str(row['skin_concerns'])
            }

            documents.append(Document(page_content=text, metadata=metadata))

        print(f"    총 {len(documents)}개의 성분 임베딩")
        return FAISS.from_documents(documents, self.embeddings)

    def _save_stores(self):
        """벡터 스토어 저장"""
        print("  - 벡터 스토어 저장 중...")
        self.products_store.save_local(str(self.vector_path / "products"))
        self.tone_store.save_local(str(self.vector_path / "tone"))
        self.reviews_store.save_local(str(self.vector_path / "reviews"))
        self.ingredients_store.save_local(str(self.vector_path / "ingredients"))

    def load_stores(self):
        """저장된 벡터 스토어 로드"""
        print("[Vector Store] 벡터 스토어 로딩 중...")

        self.products_store = FAISS.load_local(
            str(self.vector_path / "products"),
            self.embeddings,
            allow_dangerous_deserialization=True
        )
        self.tone_store = FAISS.load_local(
            str(self.vector_path / "tone"),
            self.embeddings,
            allow_dangerous_deserialization=True
        )
        self.reviews_store = FAISS.load_local(
            str(self.vector_path / "reviews"),
            self.embeddings,
            allow_dangerous_deserialization=True
        )

        # 성분 벡터 스토어 로드 (선택적)
        ingredients_path = self.vector_path / "ingredients"
        if ingredients_path.exists():
            self.ingredients_store = FAISS.load_local(
                str(ingredients_path),
                self.embeddings,
                allow_dangerous_deserialization=True
            )
        else:
            print("  ⚠ 성분 벡터 스토어가 없습니다")
            self.ingredients_store = None

        print("[Vector Store] 벡터 스토어 로딩 완료!")

    def search_products(self, query: str, k: int = 5, filters: Dict = None) -> List[Document]:
        """제품 검색"""
        return self.products_store.similarity_search(query, k=k)

    def search_tone_examples(self, brand: str, k: int = 3) -> List[Document]:
        """브랜드별 톤 예시 검색"""
        results = self.tone_store.similarity_search(
            f"{brand} 브랜드 톤",
            k=k,
            filter={"brand": brand} if brand else None
        )
        return results

    def search_reviews(self, query: str, k: int = 3) -> List[Document]:
        """유사 리뷰 검색"""
        return self.reviews_store.similarity_search(query, k=k)

    def search_ingredients(self, query: str, k: int = 5) -> List[Document]:
        """성분 검색 (피부 고민 기반)"""
        if self.ingredients_store is None:
            return []
        return self.ingredients_store.similarity_search(query, k=k)
