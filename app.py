"""
로컬 개발용 Flask 앱
"""

from api.index import app

if __name__ == '__main__':
    print("="*60)
    print("아모레퍼시픽 CRM 메시지 생성기 - 로컬 서버")
    print("="*60)
    print("\n서버 시작: http://localhost:5000")
    print("종료하려면 Ctrl+C를 누르세요\n")

    app.run(debug=True, host='0.0.0.0', port=5000)
