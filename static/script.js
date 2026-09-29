// DOM 요소
const form = document.getElementById('personaForm');
const initialState = document.getElementById('initialState');
const loadingState = document.getElementById('loadingState');
const resultState = document.getElementById('resultState');
const errorState = document.getElementById('errorState');

// 원본 데이터 저장용 변수
let originalTitle = '';
let originalBody = '';
let inputKeywords = '';
let formDataSnapshot = {}; // 모든 폼 데이터 저장

// 폼 제출 이벤트
form.addEventListener('submit', async (e) => {
    e.preventDefault();

    // 폼 데이터 수집
    const formData = new FormData(form);

    // 피부 고민 (복수 선택) 수집
    const skinConcerns = [];
    document.querySelectorAll('input[name="skin_concerns"]:checked').forEach(checkbox => {
        skinConcerns.push(checkbox.value);
    });

    // 선호 키워드 수집
    const preferredKeywords = [];
    const weatherKeyword = formData.get('weather_keyword');
    const toneKeyword = formData.get('tone_keyword');
    const usageKeyword = formData.get('usage_keyword');
    const customKeyword = formData.get('custom_keyword');

    if (weatherKeyword) preferredKeywords.push(weatherKeyword);
    if (toneKeyword) preferredKeywords.push(toneKeyword);
    if (usageKeyword) preferredKeywords.push(usageKeyword);

    // 커스텀 키워드 처리 (콤마로 구분)
    if (customKeyword && customKeyword.trim()) {
        const customKeywords = customKeyword.split(',')
            .map(keyword => keyword.trim())
            .filter(keyword => keyword.length > 0);
        preferredKeywords.push(...customKeywords);
    }

    // 입력 키워드 저장 (나중에 CSV 저장용)
    inputKeywords = preferredKeywords.join(', ');

    // 데이터 객체 생성
    const data = {
        age: parseInt(formData.get('age')),
        gender: formData.get('gender'),
        price_sensitivity: formData.get('price_sensitivity'),
        skin_type: formData.get('skin_type'),
        skin_concerns: skinConcerns.join(', '),
        product_category: formData.get('product_category'),
        preferred_brand: formData.get('preferred_brand'),
        lifestyle_keywords: preferredKeywords,  // 선호 키워드 사용
        message_purpose: 'personalized'
    };

    // 폼 데이터 스냅샷 저장 (CSV 저장용)
    formDataSnapshot = {
        age: data.age,
        gender: data.gender,
        price_sensitivity: data.price_sensitivity,
        skin_type: data.skin_type,
        skin_concerns: data.skin_concerns,
        product_category: data.product_category,
        preferred_brand: data.preferred_brand,
        lifestyle_keywords: preferredKeywords.join(', ')
    };

    // 유효성 검사
    if (!data.age) {
        alert('나이대를 선택해주세요.');
        return;
    }
    if (!data.gender) {
        alert('성별을 선택해주세요.');
        return;
    }
    if (!data.price_sensitivity) {
        alert('가격 선호도를 선택해주세요.');
        return;
    }
    if (!weatherKeyword) {
        alert('날씨 키워드를 선택해주세요.');
        return;
    }
    if (!toneKeyword) {
        alert('톤 키워드를 선택해주세요.');
        return;
    }
    if (!usageKeyword) {
        alert('용도 키워드를 선택해주세요.');
        return;
    }
    if (!data.skin_type) {
        alert('피부 타입을 선택해주세요.');
        return;
    }
    if (skinConcerns.length === 0) {
        alert('피부 고민을 하나 이상 선택해주세요.');
        return;
    }
    if (!data.product_category) {
        alert('관심 제품 카테고리를 선택해주세요.');
        return;
    }
    if (!data.preferred_brand) {
        alert('선호 브랜드를 선택해주세요.');
        return;
    }

    // UI 상태 변경: 로딩 표시
    showLoading();

    try {
        // API 호출
        const response = await fetch('/api/generate', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(data)
        });

        const result = await response.json();

        if (result.success) {
            // 성공: 결과 표시
            showResult(result.result);
        } else {
            // 실패: 에러 표시
            showError(result.error || '메시지 생성에 실패했습니다.');
        }
    } catch (error) {
        console.error('Error:', error);
        showError('서버와 통신 중 오류가 발생했습니다. 잠시 후 다시 시도해주세요.');
    }
});

// UI 상태 관리 함수들
function showLoading() {
    initialState.style.display = 'none';
    loadingState.style.display = 'block';
    resultState.style.display = 'none';
    errorState.style.display = 'none';

    // 버튼 비활성화
    const submitBtn = document.getElementById('generateBtn');
    submitBtn.disabled = true;
}

function showResult(result) {
    initialState.style.display = 'none';
    loadingState.style.display = 'none';
    resultState.style.display = 'block';
    errorState.style.display = 'none';

    // 원본 데이터 저장
    originalTitle = result.title;
    originalBody = result.body;

    // 결과 데이터 표시
    document.getElementById('resultBrand').textContent = result.brand;
    document.getElementById('messageTitle').value = result.title;
    document.getElementById('messageBody').value = result.body;

    // 제품 목록 표시
    const productsList = document.getElementById('productsList');
    productsList.innerHTML = '';
    result.products.forEach(product => {
        const li = document.createElement('li');
        li.textContent = product;
        productsList.appendChild(li);
    });

    // 버튼 활성화
    const submitBtn = document.getElementById('generateBtn');
    submitBtn.disabled = false;

    // 결과 영역으로 스크롤 (모바일 환경 고려)
    resultState.scrollIntoView({ behavior: 'smooth', block: 'start' });
}

function showError(errorMessage) {
    initialState.style.display = 'none';
    loadingState.style.display = 'none';
    resultState.style.display = 'none';
    errorState.style.display = 'block';

    document.getElementById('errorMessage').textContent = errorMessage;

    // 버튼 활성화
    const submitBtn = document.getElementById('generateBtn');
    submitBtn.disabled = false;
}

function resetForm() {
    initialState.style.display = 'block';
    loadingState.style.display = 'none';
    resultState.style.display = 'none';
    errorState.style.display = 'none';

    // 폼 초기화 (선택사항)
    // form.reset();

    // 초기 상태로 스크롤
    initialState.scrollIntoView({ behavior: 'smooth', block: 'start' });
}

// 마케팅 데이터 자산으로 저장
async function saveAsMarketingAsset() {
    // 현재 화면에 표시된 제목과 본문 가져오기 (textarea의 value)
    const currentTitle = document.getElementById('messageTitle').value;
    const currentBody = document.getElementById('messageBody').value;

    // 수정 여부 확인
    const isEdited = (currentTitle !== originalTitle) || (currentBody !== originalBody);

    // 모든 폼 데이터를 문자열로 변환
    const allFormData = JSON.stringify(formDataSnapshot);

    // 저장할 데이터
    const saveData = {
        input_keywords: allFormData,  // 모든 폼 데이터를 JSON 문자열로 저장
        original_title: originalTitle,
        original_body: originalBody,  // 원본 본문 추가
        final_title: currentTitle,
        final_body: currentBody,
        is_edited: isEdited
    };

    try {
        // API 호출
        const response = await fetch('/api/save', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(saveData)
        });

        const result = await response.json();

        if (result.success) {
            const editStatus = isEdited ? 'O (수정됨)' : 'X (원본 그대로)';
            alert(`마케팅 자산으로 등록되었습니다.\n수정 여부: ${editStatus}`);
        } else {
            alert('저장 중 오류가 발생했습니다: ' + result.error);
        }
    } catch (error) {
        console.error('Save error:', error);
        alert('저장 중 오류가 발생했습니다. 잠시 후 다시 시도해주세요.');
    }
}

// 페이지 로드 시 초기화
window.addEventListener('DOMContentLoaded', () => {
    console.log('아모레퍼시픽 CRM 메시지 생성기 로드 완료');
});
