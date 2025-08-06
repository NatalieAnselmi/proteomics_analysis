# proteomics_analysis
Localization and Functional Analysis for a given list of proteins or genes

FIRST: Get FASTA sequences for all protein
1)Go to Uniprot							
		 https://www.uniprot.org/id-mapping	
   
2) Copy paste protein list into text box
  2a) For total proteins, simply copy paste the protein IDs from the initial excel file
  2b) For proteins only over a certain SpC and TIC, run most_changed_proteins.py and use the protein list in the resulting text file							
3) Set From database: UniProtKB (for Uniprot protein ID); set To database: UniprotKB	
	To database: 	
4) Run ID Map
5) Go to customize columns at the top of the webpage, deselect all
6) Download text file (NOT fasta file) with NO compression
7) Clean file with strip-metadata.py (Removes all metadata, leaving just protein name and sequence in FASTA format in a new text file)

LOCALIZATION
1) PSORTb
   a) submit fasta list (either of total or most changed proteins) to psortb: https://psort.org/psortb/index.html
   b) results via email, output normal
  c) turn results into a Protein:Localization matrix by running clean_psort_results.py
2) SOSUI
   a) Go to https://harrier.nagahama-i-bio.ac.jp/sosui/sosuigramn/sosuigramn_submit.html
   b) Submit several proteins at a time, copy paste output to excel sheet
3) CELLO
   a) Go to https://cello.life.nctu.edu.tw/
   b) submit fasta list (either of total or most changed proteins)
   c) Save results as text file
   d) Run clean_cello_data.py to get  a file with JUST the most likely localization and protein ID 
4) Copy paste PSORTb and CELLO lists into same sheet as SOSUI results
5) Sort each by protein name and ensure proteins are aligned
6) If 2/3 sources agree on location, assume that localization is correct, save in new column
   a) could have a code do this, I just haven't written it

COG FUNCTIONAL ANALYSIS
1) Go to eggNOG tool: http://eggnog-mapper.embl.de/
2) Upload cleaned FASTA file and input email
3) Go to email from eggNOG and 'CLICK TO MANAGE YOUR JOB'
   a) May have to click start
4) When run finished, download Excel file of results; Column of interest is COG_category
5) Run create-COG-lists.py per downloaded file to get a text file of proteins sorted by COG, including counts per category
   a) Can count in excel how often each COG Code appears using    =COUNTIF($[range], "*Letter*"). Made sure to include the wildcard * on either side of the         COG letter youre searching for to account for proteins with multiple letters. Without *, a protein with CO (meaning C and O) will not be counted for           either					
6) Run compare-COGs.py to get a text file of proteins unique to a strain (can compare more than 2 files)						
7) Make your Prisim pie chart	
