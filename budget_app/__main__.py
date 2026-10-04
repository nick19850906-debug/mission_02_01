import argparse
import sys
from .service import BudgetService

def main():
    parser = argparse.ArgumentParser(description="나만의 용돈 기입장 (Budget App)")
    parser.add_argument("--data-dir", default="./data", help="데이터 저장 폴더")
    
    subparsers = parser.add_subparsers(dest="command", help="명령어")

    # add
    subparsers.add_parser("add", help="거래 추가 (대화형)")

    # list
    list_p = subparsers.add_parser("list", help="거래 목록")
    list_p.add_argument("--limit", type=int, default=10, help="출력 개수")

    # search
    search_p = subparsers.add_parser("search", help="거래 검색")
    search_p.add_argument("--from", dest="from_date")
    search_p.add_argument("--to", dest="to_date")
    search_p.add_argument("--category")
    search_p.add_argument("--type")
    search_p.add_argument("-q", dest="q", help="메모 키워드")
    search_p.add_argument("--tag")

    # summary
    sum_p = subparsers.add_parser("summary", help="월별 요약")
    sum_p.add_argument("--month", required=True, help="YYYY-MM")
    sum_p.add_argument("--top", type=int, default=3)

    # budget
    bud_p = subparsers.add_parser("budget", help="예산 관리")
    bud_sub = bud_p.add_subparsers(dest="budget_cmd")
    bset_p = bud_sub.add_parser("set")
    bset_p.add_argument("--month", required=True)
    bset_p.add_argument("--amount", type=int, required=True)

    # category
    cat_p = subparsers.add_parser("category", help="카테고리 관리")
    cat_sub = cat_p.add_subparsers(dest="cat_cmd")
    cadd_p = cat_sub.add_parser("add")
    cadd_p.add_argument("name")
    cat_sub.add_parser("list")
    crem_p = cat_sub.add_parser("remove")
    crem_p.add_argument("name")

    # update
    upd_p = subparsers.add_parser("update", help="거래 수정")
    upd_p.add_argument("--id", required=True)
    upd_p.add_argument("--date")
    upd_p.add_argument("--type")
    upd_p.add_argument("--category")
    upd_p.add_argument("--amount", type=int)
    upd_p.add_argument("--memo")
    upd_p.add_argument("--tags")

    # delete
    del_p = subparsers.add_parser("delete", help="거래 삭제")
    del_p.add_argument("--id", required=True)

    # export
    exp_p = subparsers.add_parser("export", help="CSV 내보내기")
    exp_p.add_argument("--out", required=True)
    exp_p.add_argument("--month")
    exp_p.add_argument("--from", dest="from_date")
    exp_p.add_argument("--to", dest="to_date")

    # import
    imp_p = subparsers.add_parser("import", help="CSV 가져오기")
    imp_p.add_argument("--from", dest="in_file", required=True)

    args = parser.parse_args()
    if not args.command:
        parser.print_help()
        sys.exit(0)

    service = BudgetService(args.data_dir)

    if args.command == "add":
        service.add_transaction_interactive()
    elif args.command == "list":
        service.list_transactions(limit=args.limit)
    elif args.command == "search":
        service.search_transactions(args.from_date, args.to_date, args.category, args.type, args.q, args.tag)
    elif args.command == "summary":
        service.summary(args.month, args.top)
    elif args.command == "budget":
        if args.budget_cmd == "set":
            service.budget_set(args.month, args.amount)
        else:
            bud_p.print_help()
    elif args.command == "category":
        if args.cat_cmd == "add":
            service.category_add(args.name)
        elif args.cat_cmd == "list":
            service.category_list()
        elif args.cat_cmd == "remove":
            service.category_remove(args.name)
        else:
            cat_p.print_help()
    elif args.command == "update":
        service.update_transaction(args.id, args.date, args.type, args.category, args.amount, args.memo, args.tags)
    elif args.command == "delete":
        service.delete_transaction(args.id)
    elif args.command == "export":
        service.export_csv(args.out, args.month, args.from_date, args.to_date)
    elif args.command == "import":
        service.import_csv(args.in_file)

if __name__ == "__main__":
    main()
