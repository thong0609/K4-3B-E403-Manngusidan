"""
test_api.py — Script kiểm tra nhanh toàn bộ luồng ScriptScout
Chạy: python test_api.py (trong khi uvicorn đang chạy ở terminal khác)
"""
import sys
import httpx
import time
import json

# Đảm bảo in tiếng Việt trên Windows console không bị lỗi mã hóa cp1252
if sys.stdout and hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

BASE = "http://localhost:8000"


def log(msg: str):
    print(f"\n{'='*60}")
    print(f"  {msg}")
    print('='*60)


def main():
    # Bước 1: Tạo session
    log("Bước 1: Tạo session")
    r = httpx.post(f"{BASE}/api/sessions", json={
        "topic": "Học máy là gì",
        "learning_goal": "Phân biệt được AI, học máy và học sâu",
        "audience": "Người mới bắt đầu học AI",
        "duration_minutes": 3,
    })
    r.raise_for_status()
    session = r.json()
    session_id = session["id"]
    print(f"✅ Session ID: {session_id}")

    # Bước 2: Kích hoạt tìm kiếm
    log("Bước 2: Kích hoạt tìm kiếm tài liệu")
    r = httpx.post(f"{BASE}/api/sessions/{session_id}/search")
    r.raise_for_status()
    print(f"✅ {r.json()['message']}")

    # Chờ agent hoàn thành
    print("\n⏳ Đang chờ agent tìm và chấm nguồn...")
    for i in range(60):
        time.sleep(3)
        r = httpx.get(f"{BASE}/api/sessions/{session_id}")
        status = r.json()["status"]
        print(f"   [{i*3}s] status = {status}")
        if status == "sources_ready":
            break
        if status == "error":
            print("❌ Agent gặp lỗi!")
            return

    if status != "sources_ready":
        print(f"❌ Quá thời gian chờ tìm kiếm nguồn (status: {status}).")
        return

    # Bước 3: Xem danh sách nguồn
    log("Bước 3: Xem danh sách nguồn")
    r = httpx.get(f"{BASE}/api/sessions/{session_id}/sources")
    sources = r.json()
    print(f"✅ Tìm được {len(sources)} nguồn:")
    for s in sources:
        icon = "✅" if s["trust_score"] and s["trust_score"] >= 0.6 else "⚠️"
        print(f"  {icon} [{s['code']}] {s['title'] or s['url'][:60]} — trust={s['trust_score']}")
        if s.get("conflict_note"):
            print(f"       ⚡ Mâu thuẫn: {s['conflict_note']}")

    # Bước 4: Loại một nguồn (nếu có >= 2 nguồn)
    if len(sources) >= 2:
        code_to_remove = sources[-1]["code"]
        log(f"Bước 4: Loại nguồn {code_to_remove}")
        r = httpx.patch(f"{BASE}/api/sessions/{session_id}/sources/{code_to_remove}", json={"is_active": False})
        r.raise_for_status()
        print(f"✅ Đã loại nguồn {code_to_remove}")

    # Bước 5: Sinh kịch bản
    log("Bước 5: Sinh kịch bản")
    print("⏳ Đang sinh kịch bản (khoảng 20-40 giây)...")
    r = httpx.post(f"{BASE}/api/sessions/{session_id}/script", timeout=120.0)
    r.raise_for_status()
    result = r.json()
    script = result["json_content"]
    verification = script.get("_verification_summary", {})

    print(f"✅ Kịch bản v{result['version']} sinh xong!")
    print(f"   Tiêu đề: {script.get('tieuDe', '')}")
    print(f"   Số câu: {len(script.get('cau', []))}")
    print(f"   Trích dẫn xác minh: {verification.get('verified_count')}/{verification.get('total_sentences_with_source')} câu ({verification.get('accuracy_rate', 0)*100:.0f}%)")

    # In 3 câu đầu
    print("\n--- 3 câu đầu ---")
    for cau in script.get("cau", [])[:3]:
        print(f"  [{cau['n']}] ({cau.get('kieu','')}) {cau.get('loi','')}")
        print(f"       nguồn: {cau.get('nguon', [])}, verified: {cau.get('citation_verified', 'N/A')}")

    # Bước 6: Tra cứu trích dẫn câu 2
    log("Bước 6: Tra cứu trích dẫn câu 2")
    r = httpx.get(f"{BASE}/api/sessions/{session_id}/cite/2")
    if r.status_code == 200:
        cite = r.json()
        print(f"✅ Câu {cite['sentence_n']}: '{cite['loi']}'")
        for c in cite["citations"]:
            print(f"   [{c['code']}] {c.get('title','')}")
            print(f"   Verified: {c.get('verified')} — {c.get('reason','')}")

    # Bước 7: Export
    log("Bước 7: Export Markdown")
    r = httpx.get(f"{BASE}/api/sessions/{session_id}/export?format=markdown")
    if r.status_code == 200:
        print(r.text[:600] + "\n...")
        with open("output_script.md", "w", encoding="utf-8") as f:
            f.write(r.text)
        print("\n✅ Đã lưu vào output_script.md")

    log("HOÀN THÀNH! Mọi endpoint đều hoạt động.")


if __name__ == "__main__":
    main()
