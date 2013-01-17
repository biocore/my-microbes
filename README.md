my-microbes
===========

_My Microbes_ is an early-stage-development set of tools for delivering personal microbiome results to individuals participating in microbiome sequencing studies. To run this on test data, you can do the following:

```
python scripts/personal_results.py -m test_data/map.txt -i test_data/bdiv/unweighted_unifrac_pc.txt -c test_data/arare/alpha_div_collated/ -o test_data/out/ -p test_data/prefs.txt -a test_data/otu_table.biom
```

This assumes that you're in the my-microbes directory, and that directory is in your ``PYTHONPATH``.
