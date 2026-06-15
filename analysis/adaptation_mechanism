clear all
set more off
version 17

cd ".."

cap which reghdfe
if _rc ssc install reghdfe, replace
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

capture confirm variable no_flood
if _rc gen no_flood = riverine == 0 & surface_water == 0

capture confirm variable adaptation
if _rc gen adaptation = flood_adaptation == 1

capture confirm variable distance_km
if _rc gen distance_km = distance_to_charing_cross_km

capture confirm variable affordable_housing_indicated
if _rc gen affordable_housing_indicated = affordable_housing == 1

capture confirm variable net_units_change
if _rc gen net_units_change = residential_gain - residential_loss

gen ln_units_all = ln(1 + max(net_units_change, 0))
gen dev_newbuild = inlist(lower(development_type), "new build", "new_build", "new built", "newbuilt")
gen dev_redevelopment = inlist(lower(development_type), "redevelopment")
gen dev_extension = inlist(lower(development_type), "extension")

global controls i.development_type_id i.housing_typology_id affordable_housing_indicated
global controls_scale i.development_type_id i.housing_typology_id affordable_housing_indicated ln_units_all
global fe absorb(lpa_id year_quarter)
global vce vce(cluster lpa_id)

preserve
collapse (count) n=approved (mean) approval=approved (semean) se=approved, by(riverine surface_water adaptation)
gen risk_category = "no_flood"
replace risk_category = "surface_water" if surface_water == 1
replace risk_category = "riverine" if riverine == 1
gen ci_low = approval - 1.96 * se
gen ci_high = approval + 1.96 * se
export delimited using "output/adaptation_conditional_approval_rates.csv", replace
restore

preserve
collapse (count) n=approved (mean) adaptation_share=adaptation approval=approved, by(riverine surface_water)
gen risk_category = "no_flood"
replace risk_category = "surface_water" if surface_water == 1
replace risk_category = "riverine" if riverine == 1
export delimited using "output/adaptation_share_by_risk.csv", replace
restore

eststo clear
eststo a1: reghdfe adaptation riverine surface_water distance_km $controls, $fe $vce
eststo a2: reghdfe adaptation riverine surface_water distance_km ln_units_all $controls, $fe $vce
eststo a3: reghdfe adaptation riverine surface_water distance_km ln_units_all i.development_type_id i.housing_typology_id affordable_housing_indicated if approved == 1, $fe $vce

esttab a1 a2 a3 using "output/table_adaptation_determinants.tex", replace booktabs se star(* 0.10 ** 0.05 *** 0.01) label compress stats(ymean N r2, labels("Mean dependent variable" "Observations" "R-squared")) keep(riverine surface_water distance_km ln_units_all)

eststo clear
eststo m1: reg approved riverine surface_water adaptation i.riverine#i.adaptation i.surface_water#i.adaptation, vce(cluster lpa_id)
eststo m2: reghdfe approved riverine surface_water adaptation i.riverine#i.adaptation i.surface_water#i.adaptation, absorb(lpa_id year_quarter) vce(cluster lpa_id)
eststo m3: reghdfe approved riverine surface_water adaptation i.riverine#i.adaptation i.surface_water#i.adaptation $controls, $fe $vce
eststo m4: reghdfe approved riverine surface_water adaptation i.riverine#i.adaptation i.surface_water#i.adaptation distance_km $controls, $fe $vce
eststo m5: reghdfe approved riverine surface_water adaptation i.riverine#i.adaptation i.surface_water#i.adaptation distance_km c.distance_km#i.riverine c.distance_km#i.surface_water $controls, $fe $vce

esttab m1 m2 m3 m4 m5 using "output/table_approval_adaptation_interaction.tex", replace booktabs se star(* 0.10 ** 0.05 *** 0.01) label compress stats(ymean N r2, labels("Mean dependent variable" "Observations" "R-squared")) keep(riverine surface_water adaptation 1.riverine#1.adaptation 1.surface_water#1.adaptation distance_km 1.riverine#c.distance_km 1.surface_water#c.distance_km) order(riverine surface_water adaptation 1.riverine#1.adaptation 1.surface_water#1.adaptation distance_km 1.riverine#c.distance_km 1.surface_water#c.distance_km)

est restore m5
lincom riverine
lincom riverine + 1.riverine#1.adaptation
lincom surface_water
lincom surface_water + 1.surface_water#1.adaptation

margins adaptation, over(riverine surface_water)
marginsplot, recast(scatter) xdimension(adaptation) bydimension(riverine surface_water) name(adaptation_approval, replace)
graph export "output/figure_adaptation_conditional_approval.png", replace width(2400)

reghdfe adaptation riverine surface_water distance_km ln_units_all $controls, $fe $vce
estimates store adapt_det
coefplot adapt_det, keep(riverine surface_water distance_km ln_units_all) xline(0) vertical name(adaptation_determinants, replace)
graph export "output/figure_adaptation_determinants.png", replace width(2400)

reghdfe approved adaptation i.riverine#i.adaptation i.surface_water#i.adaptation riverine surface_water distance_km $controls if riverine == 1 | surface_water == 1, $fe $vce
estimates store approval_adapt
coefplot approval_adapt, keep(adaptation 1.riverine#1.adaptation 1.surface_water#1.adaptation) xline(0) vertical name(approval_adaptation, replace)
graph export "output/figure_approval_adaptation.png", replace width(2400)
