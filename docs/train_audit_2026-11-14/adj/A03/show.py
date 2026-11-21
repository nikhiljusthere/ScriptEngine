import json,sys
P='/home/goblin/ScriptEngine/.claude/worktrees/9b-model-extraction-analysis-a7e9c9/docs/train_audit_2026-11-14/adj/A03_adj_input.jsonl'
rows=[json.loads(l) for l in open(P)]
lo,hi=int(sys.argv[1]),int(sys.argv[2])
ctx='ctx' in sys.argv
for i,d in enumerate(rows[lo:hi],lo):
    print('='*30,i,'b',d['b'],d['series'],'|',d['page'],'|',d['section'])
    if ctx:
        print('BEFORE:',str(d['page_text_before'])[-600:])
    for k,s in d['sentences'].items(): print(' S'+k+':',s)
    if ctx: print('AFTER:',str(d['page_text_after'])[:400])
    print('GE:'); [print('  ',e) for e in d['gold_events']]
    print('GF:'); [print('  ',e) for e in d['gold_facts']]
    print('GT:'); [print('  ',e) for e in d['gold_tags']]
    print('NOTES:',d['reviewer_notes'])
    print('SR:',json.dumps(d['second_reader'],ensure_ascii=False))
    print('SR_ONLY:',d['second_reader_only_events'])
    print('GOLD_ONLY:',d['gold_only_events'])
    print('OMITS:',d['gold_people_second_reader_omits'])
