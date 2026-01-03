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
        """제품 데이터 벡터 스토어 구축"""
        print("  - 제품 데이터 임베딩 중...")
        documents = []

        products_dir = self.db_path / "products_db"
        for csv_file in products_dir.glob("*_products.csv"):
            df = pd.read_csv(csv_file, encoding='utf-8-sig')

            for _, row in df.iterrows():
                # 제품 정보를 텍스트로 변환
                text = f"""
                제품명: {row['product_name']}
                카테고리: {row['category']}
                설명: {row['description']}
                주성분: {row['main_ingredients']}
                피부타입: {row['target_skin_type']}
                가격: {row['price']:,}원
                """.strip()

                metadata = {
                    "product_id": row['product_id'],
                    "product_name": row['product_name'],
                    "brand": csv_file.stem.split('_')[0],
                    "category": row['category'],
                    "price": int(row['price']),
                    "skin_type": row['target_skin_type']
                }

                documents.append(Document(page_content=text, metadata=metadata))

        return FAISS.from_documents(documents, self.embeddings)

    def _build_tone_store(self) -> FAISS:
        """브랜드 톤 코퍼스 벡터 스토어 구축"""
        print("  - 브랜드 톤 데이터 임베딩 중...")
        documents = []

        tone_dir = self.db_path / "brand_tone_corpus"
        for csv_file in tone_dir.glob("*_tone_texts.csv"):
            df = pd.read_csv(csv_file, encoding='utf-8-sig')
            brand = csv_file.stem.split('_')[0]

            for _, row in df.iterrows():
                metadata = {
                    "brand": brand,
                    "source": row['source'],
                    "tone_features": row['tone_features']
                }

                documents.append(
                    Document(page_content=row['text_content'], metadata=metadata)
                )

        return FAISS.from_documents(documents, self.embeddings)

    def _build_reviews_store(self) -> FAISS:
        """리뷰 데이터 벡터 스토어 구축 (라이프스타일 리치만)"""
        print("  - 리뷰 데이터 임베딩 중...")
        documents = []

        reviews_dir = self.db_path / "reviews_db"
        for csv_file in reviews_dir.glob("*_reviews.csv"):
            df = pd.read_csv(csv_file, encoding='utf-8-sig')

            # is_lifestyle_rich가 True인 리뷰만 선택
            lifestyle_reviews = df[df['is_lifestyle_rich'] == True]

            for _, row in lifestyle_reviews.iterrows():
                metadata = {
                    "product_id": '_'.join(csv_file.stem.split('_')[:-1]),
                    "age_group": row['age_group'],
                    "gender": row['gender'],
                    "skin_type": row['skin_type'],
                    "rating": int(row['rating'])
                }

                documents.append(
                    Document(page_content=row['review_text'], metadata=metadata)
                )

        return FAISS.from_documents(documents, self.embeddings)

    def _build_ingredients_store(self) -> FAISS:
        """화장품 성분 데이터 벡터 스토어 구축"""
        print("  - 성분 데이터 임베딩 중...")
        documents = []

        # 성분 DB 파일 경로
        ingredients_path = Path("./ingredients_db/cosmetic_ingredients.csv")

        if not ingredients_path.exists():
            print("    [경고] 성분 DB가 없습니다. 빈 스토어 생성...")
            # 빈 Document로 스토어 생성
            documents.append(Document(
                page_content="성분 정보 없음",
                metadata={"ingredient_id": "none"}
            ))
            return FAISS.from_documents(documents, self.embeddings)

        df = pd.read_csv(ingredients_path, encoding='utf-8-sig')

        for _, row in df.iterrows():
            # 성분 정보를 텍스트로 변환
            text = f"""
            성분명(한글): {row['ingredient_kor']}
            성분명(영문): {row['ingredient_eng']}
            효능: {row['function']}
            설명: {row['description']}
            관련 피부 고민: {row['skin_concerns']}
            """.strip()

            metadata = {
                "ingredient_id": row['ingredient_id'],
                "ingredient_kor": row['ingredient_kor'],
                "ingredient_eng": row['ingredient_eng'],
                "function": row['function'],
                "skin_concerns": row['skin_concerns']
            }

            documents.append(Document(page_content=text, metadata=metadata))

        print(f"    ✓ {len(documents)}개 성분 임베딩 완료")
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

        # 성분 스토어는 선택적 로드
        ingredients_path = self.vector_path / "ingredients"
        if ingredients_path.exists():
            self.ingredients_store = FAISS.load_local(
                str(ingredients_path),
                self.embeddings,
                allow_dangerous_deserialization=True
            )
        else:
            print("  [참고] 성분 벡터 스토어가 없습니다.")
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
            print("  [경고] 성분 벡터 스토어가 없습니다.")
            return []

        return self.ingredients_store.similarity_search(query, k=k)
