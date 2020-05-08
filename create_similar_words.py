# reference
# https://qiita.com/pocket_kyoto/items/1e5d464b693a8b44eda5
'''functions
csv_input: csv入力でリスト返却
SearchSimilarWords: 同義語リストを作成し返却
create_similar_wordlst: 同義語リスト整形
save_synonyms: 同義語リスト保存
'''

import sqlite3
import csv
import re
# db接続
conn = sqlite3.connect("wnjpn.db")
# ui
csvfile = 'word.csv'
outfile = 'similar_words.csv'

def csv_input(path_name):
    rows = []
    with open(path_name,encoding='utf-8') as f:
        reader = csv.reader(f)
        for row in reader:
            rows.append(row)
    return rows

def SearchSimilarWords(word):
    word = ','.join(word)
    cur = conn.execute("select wordid from word where lemma='%s'" % word)
    word_id = 99999999  #temp
    for row in cur:
        word_id = row[0]

    # Wordnetに存在する語であるかの判定
    if word_id==99999999:
        return
    cur = conn.execute("select synset from sense where wordid='%s'" % word_id)
    synsets = []
    for row in cur:
        synsets.append(row[0])
    simdict = []
    for synset in synsets:
        cur1 = conn.execute("select name from synset where synset='%s'" % synset)
        cur2 = conn.execute("select def from synset_def where (synset='%s' and lang='jpn')" % synset)
        cur3 = conn.execute("select wordid from sense where (synset='%s' and wordid!=%s)" % (synset,word_id))
        for row3 in cur3:
            target_word_id = row3[0]
            cur3_1 = conn.execute("select lemma from word where wordid=%s" % target_word_id)
            for row3_1 in cur3_1:
                # 類似語をリストに格納
                simdict.append(row3_1[0])
    return simdict

def create_similar_wordlst(full_word):
    parent = []
    child = []
    with open(csvfile, encoding='utf-8') as f:
        reader = csv.reader(f)
        for row in reader:
            child = []
            synonym = SearchSimilarWords(row)
            if not synonym is None:
                row = ','.join(row)
                child.append(row)
                for f_row in full_word:
                    f_row = ','.join(f_row)
                    for syn in synonym:
                        if f_row == syn:
                            child.append(syn)
            if len(child) > 1:
                parent.append(set(child))
    return parent

def save_synonyms(lst):
    norlst = []
    for row in lst:
        row = list(row)
        row = ','.join(row)
        norlst.append(row)
    norlst = set(norlst)
    with open(outfile, mode='w') as f:
        for row in norlst:
            f.write(row+'\n')


def main():
    full_word = csv_input(csvfile)
    save_synonyms(create_similar_wordlst(full_word))


if __name__ == "__main__":
    main()
