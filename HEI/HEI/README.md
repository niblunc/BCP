# About the Functions
# file_org
A function that is reading in all the 04 and 09 dataset and creating a single dataset called _datasetTOTAL
The other functions in HEI expect this structure
OUTPUT = dictionary of the options (ex. mom and child or just mom)
# make_components
A function that take the hei_dict (what elements are in each hei component) and the

# make_ped_components
A function that is gathering the NDSR output into the HEI or DQI components
OUTPUT = dataframe

# make_hei
This is specific for the pediatric because they have non-standard components, need to create protein, sweets, vegetables, and salty groups.
OUTPUT - dataframe

# grouper
makes both the daily and overall all hei scores. For the pediatric only want to use the raw NOT daily.

# Check
This function is taking the dictionary of parameters, the datatables and making the calculated HEI scores which are then summed for the total HEI score. This function in the pediatric data calls DQI(), in the adult data it calls adeq_check and mod_check.

# About the DQI
from Rios et al. "Development of a Diet Quality Score for Infants and Toddlers and its association with weight"J Nutrit Health Food Sci. 2016 ; 4(4): .

## Diet Quality Index Scoring for infants 0–5 months
| Component  | Scores  |
|---|---|
| Milk (type of feeding)  |   |
| Breastfeeding  | 15 (ex)  |
| Formula  |  10 (partial) |
|   |  5 (ex) |
| Cereal  | Not consumed = 5  |
|   | consumed = 0  |
| Protein  | Not consumed = 5  |
|   | consumed = 0  |
| Vegetables  | Not consumed = 5  |
|   | consumed = 0  |
| Fruits  | Not consumed = 5  |
|   | consumed = 0  |
| 100% fruit juice  | Not consumed = 5  |
|   | consumed = 0  |
| Sugar-sweetened beverages  | Not consumed = 5  |
|   | consumed = 0  |
| Sweets  | Not consumed = 5  |
|   | consumed = 0  |
| Salty snacks  | Not consumed = 5  |
|   | consumed = 0  |
| Total  | 0-55  |

The scores were based on the age of introduction of these foods as recommended by the WIC program13, the WHO14 and the American Academy of Pediatrics15, not on portion sizes.

## Diet Quality Index Scoring for infants 8-24 months
| Component  | Score  | 8-11 months  | 12-24 months  |
|---|---|---|---|
| Milk  |   |   |   |
|  Breastfeeding | 10  | Yes  | Yes  |
| Formula/Cow's milk/non-dairy milks  | 5  | 20-28  | 14-18  |
|   | 2.5  | 8.0–19.9 or 28.1–35.0  | 8.0–13.9 or 18.1–24.0  |
|   | 0  | <8 or >35  | <8.0 or >24.0  |
| Grains  |   |   |   |
|  Whole grains  | 2.5  | 1.0–3.5  | 1.5–5.5  |
|   | 1.25  |  0.1–0.9 or 3.6–8.0 |  0.1–1.4 or 5.6–8.0 |
|   |  0 | 0 or >8.0  | 0 or >8.0  |
|  Refined grains | 2.5  |  0–1.5 |  0–1.8 |
|   |  1.25 |  1.6–3.5 |  1.9–4.2 |
|   | 0  | >3.5  | >4.2  |
| Proteins  |  5 | 2.5–6.0  |  2.0–3.0 |
|   | 2.5  |  0.1–2.4 or 6.1–10.0 | 0.1–1.9 or 3.1–6.0  |
|   | 0  | 0 or >10  |  0 or >6.0 |
| Vegetables | 5  |  ≥2.0  | ≥8.0  |
|   | 2.5  |  0.1–1.9 | 0.1–7.9  |
|   |  0 |  0 |  0 |
| Fruits  | 5  | ≥2.0  | ≥8.0  |
|   | 2.5  |  0.1–1.9 | 0.1–7.9  |
|   | 0  |  0 |  0 |
| 100% fruit juice  | 5  |  0 |  0-4.0 |
|   | 2.5  | 0.1–6.0  | 4.1–6.0  |
|   |  0 | >6.0  | >6.0  |
| Sugar sweetened beverages  | 5  |  0 | 0  |
|   | 2.5  | 0.1–4.0  | 4.1–6.0  |
|   |  0 | >6.0  | >6.0  |
| Sweets  | 5  |  0 |  0 |
|   | 2.5  |  0.1-1.0 | 0.1-1.0  |
|   | 0  | >1.0  | >1.0  |
| Salty snacks  | 5  |  0 | 0  |
|   | 2.5  |  0.1-1.0 | 0.1-1.0  |
|   | 0  | >1.0  | >1.0  |
