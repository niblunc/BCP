/*********************************************************************/
/*                                                                   */
/*HEI2015 Calculator per Person NDSR 2013 or subsequent              */
/*HEI2015perpersonNDSR2013subsequent.sas                             */
/*                                                                   */
/*********************************************************************/
/*               VERSION 1.1         06/14/2019  Added total score   */
/*               VERSION 1.0         07/13/2017                      */
/*                                                                   */
/*                                                                   */
/*********************************************************************/
;

LIBNAME ndsdata 'c:\sas\sasdata' ;

/* INCLUDE THE FORMATS */
%INCLUDE 'ndsformt.sas';

proc sort data=ndsdata.fgscrecord; by cpartid dintake; 
proc sort data=ndsdata.record; by cpartid dintake;

*MERGE NDSR FILE 04 & FILE 09 DATA;
data record0409;
merge ndsdata.record ndsdata.fgscrecord;
by cpartid dintake;
run;

data hei0409; set record0409;

*ADEQUACY
** TOTAL VEGETABLES COMPONENT;
	hei_totveg=(rfgsciVEG0100+rfgsciVEG0200+rfgsciVEG0300+rfgsciVEG0400+rfgsciVEG0800+rfgsciVEG0450+rfgsciVEG0700+
		rfgsciVEG0600+rfgsciVEG0900+rfgsciVEG0500)/2; 

** GREENS AND BEANS COMPONENT;
	hei_greensbeans=(rfgsciVEG0100+rfgsciVEG0700)/2;
		
** TOTAL FRUITS COMPONENT;
	hei_totfruit=(rfgsciFRU0100+rfgsciFRU0200+rfgsciFRU0300+rfgsciFRU0400+rfgsciFRU0500+rfgsciFRU0600+rfgsciFRU0700)/2;
  
** WHOLE FRUITS COMPONENT;
	hei_wholefruit=(rfgsciFRU0300+rfgsciFRU0400+rfgsciFRU0500+rfgsciFRU0600+rfgsciFRU0700)/2;
		
** WHOLE GRAINS COMPONENT;
	hei_wholegrains=riwholegrains;
 
** DAIRY COMPONENT;** INCLUDE DAIRY GROUPS ADDED IN 2019;
	hei_dairy=(rfgsciDMF0100+rfgsciDMR0100+rfgsciDML0100+rfgsciDMN0100+rfgsciDMF0200+rfgsciDMR0200+
		rfgsciDML0200+rfgsciDML0300+rfgsciDML0400+rfgsciDCF0100+rfgsciDCR0100+rfgsciDCL0100+rfgsciDCN0100+
		rfgsciDYF0100+rfgsciDYR0100+rfgsciDYL0100+rfgsciDYF0200+rfgsciDYR0200+rfgsciDYL0200+rfgsciDYN0100+
		((rfgsciDOT0100)/3)+rfgsciDOT0300+rfgsciDOT0400+rfgsciDOT0500+rfgsciDOT0600)+
		rfgsciDML0500 + rfgsciDYF0300 + rfgsciDYR0300 + rfgsciDYL0300 + rfgsciDOT0900;
		
** TOTAL PROTEIN FOODS COMPONENT;
	hei_totproteins=(rfgsciMRF0100+rfgsciMRL0100+rfgsciMRF0200+rfgsciMRL0200+
		rfgsciMRF0300+rfgsciMRL0300+rfgsciMRF0400+rfgsciMRL0400+rfgsciMCF0200+rfgsciMCL0200+rfgsciMRF0500+
		rfgsciMPF0100+rfgsciMPL0100+rfgsciMPF0200+rfgsciMFF0100+rfgsciMFL0100+rfgsciMFF0200+rfgsciMSL0100+
		rfgsciMSF0100+rfgsciMCF0100+rfgsciMCL0100+rfgsciMOF0100+rfgsciMOF0200+rfgsciMOF0300+rfgsciMOF0400+
		rfgsciMOF0500+rfgsciMOF0600+rfgsciMOF0700+(rfgsciVEG0700*2));

** SEAFOOD AND PLANT PROTEINS COMPONENT;
	hei_seafoodplantprot=(rfgsciMFF0100+
		rfgsciMFL0100+rfgsciMFF0200+rfgsciMSL0100+rfgsciMSF0100+rfgsciMOF0500+rfgsciMOF0600+rfgsciMOF0700+
		(rfgsciVEG0700*2));
		
*MODERATION
** SODIUM COMPONENT;
	hei_sodium = rina/1000;
		
** REFINED GRAINS COMPONENT;
	hei_refinedgrains=rirefinedgrains;
	
** ADDED SUGARS COMPONENT;
	hei_addedsugars=rias_ts*4; 
run;

data hei0409togroup;
	set hei0409;
	ripctsfa = ripctsfa*rikcal;

proc means data=hei0409togroup noprint;
  by cpartid;
  var rikcal hei_totveg hei_greensbeans hei_totfruit hei_wholefruit hei_wholegrains hei_dairy hei_totproteins hei_seafoodplantprot 
		ripfa rimfa risfa hei_sodium hei_refinedgrains hei_addedsugars ripctsfa;
  output out=dailyhei0409 sum=;
run;

data hei0409;
	set dailyhei0409;
	ripctsfa = ripctsfa/rikcal ;


data hei0409; 
   set hei0409; 

energy=rikcal/1000;
if rikcal=0 then do;
  HEIX1_TOTALVEG=0; HEIX2_GREEN_AND_BEAN=0; HEIX3_TOTALFRUIT=0; HEIX4_WHOLEFRUIT=0; HEIX5_WHOLEGRAIN=0; HEIX6_TOTALDAIRY=0;
  HEIX7_TOTPROT=0;  HEIX8_SEAPLANT_PROT=0; HEIX9_FATTYACID=0; HEIX10_SODIUM=0; HEIX11_REFINEDGRAIN=0; HEIX12_ADDEDSUGARS=0; 
  HEIX13_SATFATS=0;
  end;
else do;

*ADEQUACY
** TOTAL VEGETABLES COMPONENT;
	xhei_totveg=hei_totveg/energy; 
		
	if xhei_totveg=0 then HEIX1_TOTALVEG=0;
		else if xhei_totveg>=1.1 then HEIX1_TOTALVEG=5;
		else HEIX1_TOTALVEG=5*(xhei_totveg/1.1);

** GREENS AND BEANS COMPONENT;
	xhei_greensbeans=hei_greensbeans/energy;
	
	if xhei_greensbeans=0 then HEIX2_GREEN_AND_BEAN=0;
		else if xhei_greensbeans>=0.2 then HEIX2_GREEN_AND_BEAN=5;
		else HEIX2_GREEN_AND_BEAN=5*(xhei_greensbeans/0.2);
		
** TOTAL FRUITS COMPONENT;
	xhei_totfruit = hei_totfruit/energy;
	
	if xhei_totfruit=0 then HEIX3_TOTALFRUIT=0;
		else if xhei_totfruit>=0.8 then HEIX3_TOTALFRUIT=5;
		else HEIX3_TOTALFRUIT=5*(xhei_totfruit/0.8);
  
** WHOLE FRUITS COMPONENT;
	xhei_wholefruit=hei_wholefruit/energy;
	
	if xhei_wholefruit=0 then HEIX4_WHOLEFRUIT=0;
		else if xhei_wholefruit>=0.4 then HEIX4_WHOLEFRUIT=5;
		else HEIX4_WHOLEFRUIT=5*(xhei_wholefruit/0.4);
		
** WHOLE GRAINS COMPONENT;
	xhei_wholegrains=hei_wholegrains/energy;
	
	if xhei_wholegrains=0 then HEIX5_WHOLEGRAIN=0;
		else if xhei_wholegrains>=1.5 then HEIX5_WHOLEGRAIN=10;
		else HEIX5_WHOLEGRAIN=10*(xhei_wholegrains/1.5);
 
** DAIRY COMPONENT;
	xhei_dairy=hei_dairy/energy;
	
	if xhei_dairy=0 then HEIX6_TOTALDAIRY=0;
		else if xhei_dairy>=1.3 then HEIX6_TOTALDAIRY=10;
		else HEIX6_TOTALDAIRY=10*(xhei_dairy/1.3);
		
** TOTAL PROTEIN FOODS COMPONENT;
	xhei_totproteins=hei_totproteins/energy;

	if xhei_totproteins=0 then HEIX7_TOTPROT=0;
		else if xhei_totproteins>=2.5 then HEIX7_TOTPROT=5;
		else HEIX7_TOTPROT=5*(xhei_totproteins/2.5);

** SEAFOOD AND PLANT PROTEINS COMPONENT;
	xhei_seafoodplantprot=hei_seafoodplantprot/energy;

	if xhei_seafoodplantprot=0 then  HEIX8_SEAPLANT_PROT=0;
		else if xhei_seafoodplantprot>=0.8 then  HEIX8_SEAPLANT_PROT=5;
		else HEIX8_SEAPLANT_PROT=5*(xhei_seafoodplantprot/0.8);
		
** FATTY ACIDS COMPONENT;
	xhei_fatacid=(ripfa+rimfa)/risfa;
	
	FARMIN=1.2;
	FARMAX=2.5;
 	if xhei_fatacid=<FARMIN then HEIX9_FATTYACID=0;
		else if xhei_fatacid>FARMAX then HEIX9_FATTYACID=10;
		else HEIX9_FATTYACID=10*((xhei_fatacid-FARMIN) / (FARMAX-FARMIN));
		
*MODERATION
** SODIUM COMPONENT;
	xhei_sodium=hei_sodium/energy;
	
	SODMIN=1.1;
	SODMAX=2.0;
 	if xhei_sodium>=SODMAX then HEIX10_SODIUM=0;
		else if xhei_sodium=<SODMIN then HEIX10_SODIUM=10;
		else HEIX10_SODIUM=10 - (10*((xhei_sodium-SODMIN) / (SODMAX-SODMIN)));
		
** REFINED GRAINS COMPONENT;
	xhei_refinedgrains=hei_refinedgrains/energy;
	
	RGMIN=1.8;
	RGMAX=4.3;
    if xhei_refinedgrains>=RGMAX then HEIX11_REFINEDGRAIN=0;
		else if xhei_refinedgrains=<RGMIN then HEIX11_REFINEDGRAIN=10;
		else HEIX11_REFINEDGRAIN=10 - (10*((xhei_refinedgrains-RGMIN) / (RGMAX-RGMIN)));

** ADDED SUGARS COMPONENT;
	xhei_addedsugars=100*hei_addedsugars/rikcal;
	
	ADDSUGMIN=6.5;
	ADDSUGMAX=26;
	if xhei_addedsugars>=ADDSUGMAX then HEIX12_ADDEDSUGARS=0;
		else if xhei_addedsugars<ADDSUGMIN then HEIX12_ADDEDSUGARS=10;
		else HEIX12_ADDEDSUGARS=10 - (10*((xhei_addedsugars-ADDSUGMIN) / (ADDSUGMAX-ADDSUGMIN)));
	
** SATURATED FAT COMPONENT;
	xhei_satfats=ripctsfa;
	
	SATFATSMIN=8;
	SATFATSMAX=16;
	if xhei_satfats>SATFATSMAX then HEIX13_SATFATS=0;
		else if xhei_satfats<SATFATSMIN then HEIX13_SATFATS=10;
		else HEIX13_SATFATS=10 - (10*((xhei_satfats-SATFATSMIN) / (SATFATSMAX-SATFATSMIN)));

end; /* KCAL > 0 */

HEI2015_TOTAL_SCORE = HEIX1_TOTALVEG + HEIX2_GREEN_AND_BEAN + HEIX3_TOTALFRUIT + HEIX4_WHOLEFRUIT + 
    HEIX5_WHOLEGRAIN + HEIX6_TOTALDAIRY + HEIX7_TOTPROT + HEIX8_SEAPLANT_PROT + HEIX9_FATTYACID + 
	HEIX10_SODIUM + HEIX11_REFINEDGRAIN + HEIX12_ADDEDSUGARS + HEIX13_SATFATS;

run;

data hei0409;
set hei0409;

label 
	hei_totveg='total vegetable servings in cup equivalents'
	hei_greensbeans='greens and beans servings in cup equivalents'
	hei_totfruit='total fruit servings in cup equivalents'
	hei_wholefruit='whole fruit servings in cup equivalents'
	hei_dairy='dairy servings in cup equivalents'
	hei_wholegrains='whole grain servings in ounce equivalents'
	hei_totproteins='total protein servings in ounce equivalents'
	hei_seafoodplantprot='sea food and plant protein servings in ounce equivalents'
	hei_refinedgrains='refined grains in ounce equivalents'
	hei_sodium ='sodium intake in grams'
	hei_addedsugars='kcal from added sugars'
	
	xhei_totfruit='total fruit servings in cup equivalents PER 1000 KCAL'
	xhei_wholefruit='whole fruit servings in cup equivalents PER 1000 KCAL'
	xhei_totveg='total vegetable servings in cup equivalents PER 1000 KCAL'
	xhei_greensbeans='greens and beans servings in cup equivalents PER 1000 KCAL'
	xhei_wholegrains='whole grain servings in ounce equivalents PER 1000 KCAL'
	xhei_dairy='dairy servings in cup equivalents PER 1000 KCAL'
	xhei_totproteins='protein servings in ounce equivalents PER 1000 KCAL'
	xhei_seafoodplantprot='sea food and plant protein servings in ounce equivalents PER 1000 KCAL'
	xhei_refinedgrains='refined grains in ounce equivalents PER 1000 KCAL' 
	xhei_sodium='sodium intake in grams PER 1000 KCAL' 
	xhei_fatacid='fatty acid ratio'
	xhei_addedsugars='percent kcal from added sugars'
	xhei_satfats='percent saturated fatty acids';

label HEI2015_TOTAL_SCORE='HEI-2015 TOTAL SCORE'
      HEIX1_TOTALVEG='HEI-2015 COMPONENT 1 TOTAL VEGETABLES (0-5)'
      HEIX2_GREEN_AND_BEAN='HEI-2015 COMPONENT 2 GREENS AND BEANS (0-5)'
      HEIX3_TOTALFRUIT='HEI-2015 COMPONENT 3 TOTAL FRUIT (0-5)'
      HEIX4_WHOLEFRUIT='HEI-2015 COMPONENT 4 WHOLE FRUIT (0-5)'
      HEIX5_WHOLEGRAIN='HEI-2015 COMPONENT 5 WHOLE GRAINS (0-10)'
      HEIX6_TOTALDAIRY='HEI-2015 COMPONENT 6 DAIRY (0-10)'
      HEIX7_TOTPROT='HEI-2015 COMPONENT 7 TOTAL PROTEIN FOODS (0-5)'
      HEIX8_SEAPLANT_PROT='HEI-2015 COMPONENT 8 SEAFOOD AND PLANT PROTEIN (0-5)'
      HEIX9_FATTYACID='HEI-2015 COMPONENT 9 FATTY ACID RATIO (0-10)'
      HEIX10_SODIUM='HEI-2010 COMPONENT 10 SODIUM (0-10)'
      HEIX11_REFINEDGRAIN='HEI-2015 COMPONENT 11 REFINED GRAINS (0-10)'
	  HEIX12_ADDEDSUGARS='HEI-2015 COMPONENT 12 ADDED SUGARS (0-10)'
	  HEIX13_SATFATS='HEI-2015 COMPONENT 13 SATURATED FATS (0-10)';
run;

* DELETE IRRELEVANT VARIABLES;
data hei0409; set hei0409; 
	drop FARMIN FARMAX RGMIN RGMAX  SODMIN SODMAX
		 ADDSUGMIN ADDSUGMAX SATFATSMIN SATFATSMAX;
run;

proc print; title 'scores by individual ID number';
var cpartid rikcal
	HEI2015_TOTAL_SCORE HEIX1_TOTALVEG HEIX2_GREEN_AND_BEAN HEIX3_TOTALFRUIT HEIX4_WHOLEFRUIT HEIX5_WHOLEGRAIN
	HEIX6_TOTALDAIRY HEIX7_TOTPROT HEIX8_SEAPLANT_PROT HEIX9_FATTYACID HEIX10_SODIUM HEIX11_REFINEDGRAIN 
	HEIX12_ADDEDSUGARS HEIX13_SATFATS;
  run;


* KEEP HEI RELATED VARIABLES;
data keephei; set hei0409;
keep cpartid rikcal
	HEI2015_TOTAL_SCORE HEIX1_TOTALVEG HEIX2_GREEN_AND_BEAN HEIX3_TOTALFRUIT HEIX4_WHOLEFRUIT HEIX5_WHOLEGRAIN
	HEIX6_TOTALDAIRY HEIX7_TOTPROT HEIX8_SEAPLANT_PROT HEIX9_FATTYACID HEIX10_SODIUM HEIX11_REFINEDGRAIN
	HEIX12_ADDEDSUGARS HEIX13_SATFATS hei_totveg hei_greensbeans hei_totfruit hei_wholefruit hei_dairy
	hei_wholegrains hei_totproteins hei_seafoodplantprot hei_refinedgrains hei_sodium hei_addedsugars 
	xhei_totfruit xhei_wholefruit xhei_totveg xhei_greensbeans xhei_wholegrains xhei_dairy xhei_totproteins
	xhei_seafoodplantprot xhei_refinedgrains xhei_fatacid xhei_sodium xhei_addedsugars xhei_satfats;
	run;

* CREATE PERMANENT DATASET WITH HEI SCORES FOR EACH ID;
data ndsdata.NDSRHEIBYID;
set keephei;
run;
