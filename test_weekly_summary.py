from datetime import date, timedelta
from weekly_summary import (
    weekly_summary, get_week_range,
    load_calorie_records, load_todo_records,
)


# 샘플 CSV와 같은 데이터
CAL = [
    {"date": date(2026, 10, 11), "type": "burn",   "name": "전주 일요일 운동",   "kcal": 200},
    {"date": date(2026, 10, 12), "type": "intake", "name": "아침 샐러드",        "kcal": 350},
    {"date": date(2026, 10, 12), "type": "burn",   "name": "러닝 30분",          "kcal": 300},
    {"date": date(2026, 10, 14), "type": "intake", "name": "닭가슴살 도시락",    "kcal": 520},
    {"date": date(2026, 10, 18), "type": "intake", "name": "저녁 식사",          "kcal": 700},
    {"date": date(2026, 10, 19), "type": "intake", "name": "다음 주 첫날 식사",  "kcal": 600},
]

# 임의로 만든 할 일 샘플
TODO = [
    {"date": date(2026, 10, 11), "title": "스트레칭", "done": True},
    {"date": date(2026, 10, 13), "title": "스쿼트",   "done": True},
    {"date": date(2026, 10, 15), "title": "물 2L",    "done": False},
    {"date": date(2026, 10, 18), "title": "다음 주 계획", "done": True},  # 다음 주
]


def test_week_range():
    assert get_week_range(date(2026, 10, 11)) == (date(2026, 10, 11), date(2026, 10, 17))  # 일
    assert get_week_range(date(2026, 10, 14)) == (date(2026, 10, 11), date(2026, 10, 17))  # 수
    assert get_week_range(date(2026, 10, 17)) == (date(2026, 10, 11), date(2026, 10, 17))  # 토
    assert get_week_range(date(2026, 10, 18)) == (date(2026, 10, 18), date(2026, 10, 24))  # 다음 일


def test_calorie_values():
    c = weekly_summary(CAL, TODO, date(2026, 10, 14))["calorie"]
    assert (c["intake"], c["burn"], c["net"]) == (870, 500, 370)
    assert len(c["records"]) == 4


def test_same_result_any_day_of_week():
    base = date(2026, 10, 11)
    results = [weekly_summary(CAL, TODO, base + timedelta(days=i)) for i in range(7)]
    for r in results:
        assert r["calorie"]["intake"] == 870
        assert r["calorie"]["burn"] == 500
        assert r["todo"]["total"] == 3


def test_week_boundary():
    nxt = weekly_summary(CAL, TODO, date(2026, 10, 18))
    assert nxt["calorie"]["intake"] == 1300 and nxt["calorie"]["burn"] == 0
    assert nxt["todo"]["total"] == 1


def test_todo_values():
    t = weekly_summary(CAL, TODO, date(2026, 10, 14))["todo"]
    assert (t["total"], t["done"], t["rate"]) == (3, 2, 67)


def test_empty_and_no_todo_file():
    empty = weekly_summary([], [], date(2026, 10, 14))
    assert empty["calorie"]["net"] == 0 and empty["todo"]["rate"] == 0
    assert weekly_summary(CAL, None, date(2026, 10, 14))["todo"] is None


def test_string_date_input():
    # 메인 화면에서 'YYYY-MM-DD' 문자열로 넘어오는 경우
    assert weekly_summary(CAL, TODO, "2026-10-14")["calorie"]["net"] == 370

def test_real_files():
    cal = load_calorie_records()   # data/sample/calories.csv
    todo = load_todo_records()     # data/sample/todo.csv
    assert len(cal) == 6
    assert todo is not None and len(todo) == 4

    r = weekly_summary(cal, todo, "2026-10-14")
    c, t = r["calorie"], r["todo"]
    assert (c["intake"], c["burn"], c["net"]) == (870, 500, 370)
    assert (t["total"], t["done"], t["rate"]) == (3, 2, 67)


if __name__ == "__main__":
    for name, fn in list(globals().items()):
        if name.startswith("test_"):
            fn()
            print("통과:", name)
    print("모든 테스트 통과")
