@echo off

REM Run data scra[er]
python Generator\utils\data_scrape.py

REM Run merged PRs script
python Generator\utils\mergedprs.py

REM Run construct counts graph script
python Generator\utils\graphing\construct_counts_graph.py

REM Run line PRs graph script
python Generator\utils\graphing\line_prs_graph.py

REM Run lines graph script
python Generator\utils\graphing\lines_graph.py

REM Run top libraries graph script
python Generator\utils\graphing\top_libraries_graph.py

REM Run word cloud script
python Generator\utils\graphing\word_cloud.py

REM Run commit heatmap script
python Generator\utils\graphing\commit_heatmap.py

REM Run File Types graph script
python Generator\utils\graphing\file_types_bar_graph.py

REM Run GIF maker script
python Generator\utils\gifmaker.py

REM Run README updater script
python Generator\readme.py

REM End of script
echo All scripts executed.
