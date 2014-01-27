# -*- coding: utf-8 -*-
import sys
sys.path.append("libs")

import proso.django

def main(argv):
    proso.django.json2csv(
        model_name=argv[0],
        json_file=argv[1],
        csv_file=argv[2]
    )

if __name__ == "__main__":
    main(sys.argv[1:])
