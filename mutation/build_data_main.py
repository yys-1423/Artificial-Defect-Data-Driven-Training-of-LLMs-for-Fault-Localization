import csv

from build_data import build_class_mutation_data
from build_data_from_mutation import build_data_from_mutation

from apply_coverage import apply_coverage




def build_data_main(p):
    csv_path = f"/home/yinseok/lorafl/data_preprocess/data_original/{p}/classes.csv"
    rows = []
    try:
        with open(csv_path, newline='', encoding='utf-8') as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                rows.append(row)
    except FileNotFoundError:
        print(f"File not found: {csv_path}")
    targets = []
    for r in rows:
        if r["category"]=="2" or r["category"]==3:
            target = r["packageName"]+"."+r["name"]
            targets.append(target)

    for t in targets:
        print(t)
        try:
            #build_class_mutation_data(p,t)
            build_data_from_mutation(p,t,30)
            apply_coverage(p,t)
            #return
        except Exception as e:
            print(e)
build_data_main("Chart")
#build_data_main("Math")
build_data_main("Lang")
build_data_main("Time")
#build_data("Closure","com.google.javascript.jscomp.graph.FixedPointGraphTraversal")
