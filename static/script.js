// DOM 요소
const form = document.getElementById('personaForm');
const initialState = document.getElementById('initialState');
const loadingState = document.getElementById('loadingState');
const resultState = document.getElementById('resultState');
const errorState = document.getElementById('errorState');

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

    if (weatherKeyword) preferredKeywords.push(weatherKeyword);
    if (toneKeyword) preferredKeywords.push(toneKeyword);
    if (usageKeyword) preferredKeywords.push(usageKeyword);

    // 데이터 객체 생성
    const data = {
        age: parseInt(formData.get('age')),
        skin_type: formData.get('skin_type'),
        skin_concerns: skinConcerns.join(', '),
        product_category: formData.get('product_category'),
        preferred_brand: formData.get('preferred_brand'),
        lifestyle_keywords: preferredKeywords,  // 선호 키워드 사용
        message_purpose: 'personalized'
    };

    // 유효성 검사
    if (!data.age) {
        alert('나이대를 선택해주세요.');
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

    // 결과 데이터 표시
    document.getElementById('resultBrand').textContent = result.brand;
    document.getElementById('messageTitle').textContent = result.title;
    document.getElementById('messageBody').textContent = result.body;

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

// 페이지 로드 시 초기화
window.addEventListener('DOMContentLoaded', () => {
    console.log('아모레퍼시픽 CRM 메시지 생성기 로드 완료');
});
