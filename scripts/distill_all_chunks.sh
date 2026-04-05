for i in {0..39}; do
    if [ ! -f "data/distillations/necro_chunk_$i.json" ]; then
        batch_distill_source --chunk_id $i --model 120B Thinker
    fi
done