clear all
set more off
version 17

cd ".."

cap which reghdfe
if _rc ssc install reghdfe, replace
cap which ftools
if _rc ssc install ftools, replace
cap which esttab
if _rc ssc install estout, replace

import delimited "data/analysis_sample.csv", clear varn(1) case(lower) encoding(utf-8)

capture confirm variable year_quarter
if _rc gen year_quarter = yq(year, quarter)
format year_quarter %tq

capture confirm variable lpa_id
if _rc encode lpa, gen(lpa_id)

capture confirm variable development_type_id
if _rc encode development_type, gen(development_type_id)

capture confirm variable housing_typology_id
if _rc encode housing_typology, gen(housing_typology_id)

capture confirm variable approved
if _rc gen approved = inlist(lower(decision), "approved", "grant", "granted", "permitted")

capture confirm variable riverine
if _rc gen riverine = flood_risk_category == "riverine"

capture confirm variable surface_water
if _rc gen surface_water = flood_risk_category == "surface_water"

capture confirm variable distance_km
if _rc gen distance_km = distance_to_charing_cross_km

capture confirm variable affordable_housing_indicated
if _rc gen affordable_housing_indicated = affordable_housing == 1

capture confirm variable net_units_change
if _rc gen net_units_change = residential_gain - residential_loss

gen ln_units = ln(1 + net_units_change) if net_units_change > 0
gen asinh_units = asinh(net_units_change)

global controls i.development_type_id i.housing_typology_id affordable_housing_indicated
global fe absorb(lpa_id year_quarter)
global vce vce(cluster lpa_id)

eststo clear
eststo m1: reg approved riverine surface_water, vce(cluster lpa_id)
eststo m2: reghdfe approved riverine surface_water, absorb(lpa_id year_quarter) vce(cluster lpa_id)
eststo m3: reghdfe approved riverine surface_water $controls, $fe $vce
eststo m4: reghdfe approved riverine surface_water distance_km $controls, $fe $vce
eststo m5: reghdfe approved riverine surface_water distance_km c.distance_km#i.riverine c.distance_km#i.surface_water $controls, $fe $vce

esttab m1 m2 m3 m4 m5 using "output/table_approval.tex", replace booktabs se star(* 0.10 ** 0.05 *** 0.01) label compress stats(ymean N r2, labels("Mean dependent variable" "Observations" "R-squared")) keep(riverine surface_water distance_km 1.riverine#c.distance_km 1.surface_water#c.distance_km) order(riverine surface_water distance_km 1.riverine#c.distance_km 1.surface_water#c.distance_km)

eststo clear
eststo m1: reg ln_units riverine surface_water if approved == 1 & net_units_change > 0, vce(cluster lpa_id)
eststo m2: reghdfe ln_units riverine surface_water if approved == 1 & net_units_change > 0, absorb(lpa_id year_quarter) vce(cluster lpa_id)
eststo m3: reghdfe ln_units riverine surface_water $controls if approved == 1 & net_units_change > 0, $fe $vce
eststo m4: reghdfe ln_units riverine surface_water distance_km $controls if approved == 1 & net_units_change > 0, $fe $vce
eststo m5: reghdfe ln_units riverine surface_water distance_km c.distance_km#i.riverine c.distance_km#i.surface_water $controls if approved == 1 & net_units_change > 0, $fe $vce

esttab m1 m2 m3 m4 m5 using "output/table_intensity.tex", replace booktabs se star(* 0.10 ** 0.05 *** 0.01) label compress stats(ymean N r2, labels("Mean dependent variable" "Observations" "R-squared")) keep(riverine surface_water distance_km 1.riverine#c.distance_km 1.surface_water#c.distance_km) order(riverine surface_water distance_km 1.riverine#c.distance_km 1.surface_water#c.distance_km)

eststo clear
probit approved riverine surface_water
margins, dydx(riverine surface_water) post
eststo p1
probit approved riverine surface_water i.lpa_id i.year_quarter
margins, dydx(riverine surface_water) post
eststo p2
probit approved riverine surface_water $controls i.lpa_id i.year_quarter
margins, dydx(riverine surface_water) post
eststo p3
probit approved riverine surface_water distance_km $controls i.lpa_id i.year_quarter
margins, dydx(riverine surface_water distance_km) post
eststo p4
probit approved riverine surface_water distance_km c.distance_km#i.riverine c.distance_km#i.surface_water $controls i.lpa_id i.year_quarter
margins, dydx(riverine surface_water distance_km) post
eststo p5

esttab p1 p2 p3 p4 p5 using "output/table_probit_ame.tex", replace booktabs se star(* 0.10 ** 0.05 *** 0.01) label compress

eststo clear
logit approved riverine surface_water
margins, dydx(riverine surface_water) post
eststo l1
logit approved riverine surface_water i.lpa_id i.year_quarter
margins, dydx(riverine surface_water) post
eststo l2
logit approved riverine surface_water $controls i.lpa_id i.year_quarter
margins, dydx(riverine surface_water) post
eststo l3
logit approved riverine surface_water distance_km $controls i.lpa_id i.year_quarter
margins, dydx(riverine surface_water distance_km) post
eststo l4
logit approved riverine surface_water distance_km c.distance_km#i.riverine c.distance_km#i.surface_water $controls i.lpa_id i.year_quarter
margins, dydx(riverine surface_water distance_km) post
eststo l5

esttab l1 l2 l3 l4 l5 using "output/table_logit_ame.tex", replace booktabs se star(* 0.10 ** 0.05 *** 0.01) label compress

eststo clear
eststo m1: reg asinh_units riverine surface_water if approved == 1, vce(cluster lpa_id)
eststo m2: reghdfe asinh_units riverine surface_water if approved == 1, absorb(lpa_id year_quarter) vce(cluster lpa_id)
eststo m3: reghdfe asinh_units riverine surface_water $controls if approved == 1, $fe $vce
eststo m4: reghdfe asinh_units riverine surface_water distance_km $controls if approved == 1, $fe $vce
eststo m5: reghdfe asinh_units riverine surface_water distance_km c.distance_km#i.riverine c.distance_km#i.surface_water $controls if approved == 1, $fe $vce

esttab m1 m2 m3 m4 m5 using "output/table_asinh_intensity.tex", replace booktabs se star(* 0.10 ** 0.05 *** 0.01) label compress stats(ymean N r2, labels("Mean dependent variable" "Observations" "R-squared")) keep(riverine surface_water distance_km 1.riverine#c.distance_km 1.surface_water#c.distance_km) order(riverine surface_water distance_km 1.riverine#c.distance_km 1.surface_water#c.distance_km)
