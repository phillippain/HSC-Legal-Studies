# Evidence Organiser — proposed tidy-up

113 files would move. **Nothing has been moved.** No file is deleted: duplicates
go to `_duplicates/` with their original path underneath, so every change is reversible.

| Change | Files | What it does |
|---|---|---|
| Rename | 23 | `%20` and `%5B` in a filename become the space and bracket they stand for |
| File | 26 | a loose document in `Cases/` or `News Articles/` moves into its topic subfolder |
| Duplicate | 63 | a second copy of the same file in the same format moves to `_duplicates/` |
| Not Legal Studies | 1 | moves to `_not-legal-studies/` |

9 loose files stay where they are because no topic can be read from the name:

- `News Articles/NSW Adult Crime Adult Time Daily 8Sept26.pdf`
- `Cases/Devine and Kitson 2026 ARTA 1944 - Case Summary.pdf`
- `Cases/F260100.rtf`
- `Cases/Glancey and Glancey 2026 ARTA 1945 - Case Summary.pdf`
- `Cases/HGY v Secretary, Ministry of Health in respect of Northern NSW Local Health District [NSW Caselaw].pdf`
- `Cases/J261054.rtf`
- `Cases/J261074.rtf`
- `Cases/Palgrave and Blackwall 2026 ARTA 1947 - Case Summary.pdf`
- `News Articles/Number of NSW children in youth detention up by one third, new data shows | New South Wales | The Guardian.pdf-Phillip Pain MacBook`

## Renames (23)

- `Cases/Human Rights/2208816(Refugee)%5B2026%5DARTA1391(2March2026).rtf`  
  → `Cases/Human Rights/2208816(Refugee)[2026]ARTA1391(2March2026).rtf`  
  _url-encoded name_
- `Cases/Human Rights/2535647(Refugee)%5B2026%5DARTA1395(20February2026).rtf`  
  → `Cases/Human Rights/2535647(Refugee)[2026]ARTA1395(20February2026).rtf`  
  _url-encoded name_
- `Jade Cases/Raw Cases/Attar%20&%20Chawd%20%5B2026%5D%20FedCFamC2F%201012.rtf`  
  → `Jade Cases/Raw Cases/Attar & Chawd [2026] FedCFamC2F 1012.rtf`  
  _url-encoded name_
- `Jade Cases/Raw Cases/Beitel%20&%20Beitel%20%20%5B2026%5D%20FedCFamC1F%20495.rtf`  
  → `Jade Cases/Raw Cases/Beitel & Beitel [2026] FedCFamC1F 495.rtf`  
  _url-encoded name_
- `Jade Cases/Raw Cases/Bergsma%20&%20Hyde%20%5B2026%5D%20FedCFamC1A%20148.rtf`  
  → `Jade Cases/Raw Cases/Bergsma & Hyde [2026] FedCFamC1A 148.rtf`  
  _url-encoded name_
- `Jade Cases/Raw Cases/Burke%20&%20Morgan%20(No%203)%20%5B2026%5D%20FedCFamC1F%20468.rtf`  
  → `Jade Cases/Raw Cases/Burke & Morgan (No 3) [2026] FedCFamC1F 468.rtf`  
  _url-encoded name_
- `Jade Cases/Raw Cases/Cadel%20&%20Galea%20%5B2026%5D%20FedCFamC1A%20142.rtf`  
  → `Jade Cases/Raw Cases/Cadel & Galea [2026] FedCFamC1A 142.rtf`  
  _url-encoded name_
- `Jade Cases/Raw Cases/Daniels%20&%20Rooney%20%5B2026%5D%20FedCFamC2F%20896.rtf`  
  → `Jade Cases/Raw Cases/Daniels & Rooney [2026] FedCFamC2F 896.rtf`  
  _url-encoded name_
- `Jade Cases/Raw Cases/Duff%20&%20Horner%20%5B2026%5D%20FedCFamC2F%201077.rtf`  
  → `Jade Cases/Raw Cases/Duff & Horner [2026] FedCFamC2F 1077.rtf`  
  _url-encoded name_
- `Jade Cases/Raw Cases/Duffy%20&%20Duffy%20%5B2026%5D%20FedCFamC2F%201076.rtf`  
  → `Jade Cases/Raw Cases/Duffy & Duffy [2026] FedCFamC2F 1076.rtf`  
  _url-encoded name_
- `Jade Cases/Raw Cases/Eadgar%20&%20Amiri%20%5B2026%5D%20FedCFamC1F%20474.rtf`  
  → `Jade Cases/Raw Cases/Eadgar & Amiri [2026] FedCFamC1F 474.rtf`  
  _url-encoded name_
- `Jade Cases/Raw Cases/Escarro%20&%20Kopp%20%5B2026%5D%20FedCFamC1F%20488.rtf`  
  → `Jade Cases/Raw Cases/Escarro & Kopp [2026] FedCFamC1F 488.rtf`  
  _url-encoded name_
- `Jade Cases/Raw Cases/Fry%20&%20Read%20(No%202)%20%5B2026%5D%20FedCFamC1F%20505.rtf`  
  → `Jade Cases/Raw Cases/Fry & Read (No 2) [2026] FedCFamC1F 505.rtf`  
  _url-encoded name_
- `Jade Cases/Raw Cases/Harlow%20&%20Harlow%20(No%203)%20%5B2026%5D%20FedCFamC1F%20527.rtf`  
  → `Jade Cases/Raw Cases/Harlow & Harlow (No 3) [2026] FedCFamC1F 527.rtf`  
  _url-encoded name_
- `Jade Cases/Raw Cases/Hemswold%20&%20Hemswold%20%5B2026%5D%20FedCFamC2F%20264.rtf`  
  → `Jade Cases/Raw Cases/Hemswold & Hemswold [2026] FedCFamC2F 264.rtf`  
  _url-encoded name_
- `Jade Cases/Raw Cases/Lagounov%20&%20Karstensen%20%5B2026%5D%20FedCFamC1F%20524.rtf`  
  → `Jade Cases/Raw Cases/Lagounov & Karstensen [2026] FedCFamC1F 524.rtf`  
  _url-encoded name_
- `Jade Cases/Raw Cases/Melzer%20&%20Powles%20(No%202)%20%5B2026%5D%20FedCFamC1F%20482.rtf`  
  → `Jade Cases/Raw Cases/Melzer & Powles (No 2) [2026] FedCFamC1F 482.rtf`  
  _url-encoded name_
- `Jade Cases/Raw Cases/Merran%20&%20Salter%20%5B2026%5D%20FedCFamC2F%201058.rtf`  
  → `Jade Cases/Raw Cases/Merran & Salter [2026] FedCFamC2F 1058.rtf`  
  _url-encoded name_
- `Jade Cases/Raw Cases/Peak%20&%20Peak%20(No%203)%20%5B2026%5D%20FedCFamC1F%20553.rtf`  
  → `Jade Cases/Raw Cases/Peak & Peak (No 3) [2026] FedCFamC1F 553.rtf`  
  _url-encoded name_
- `Jade Cases/Raw Cases/Pratley%20&%20Pratley%20(No%209)%20%5B2026%5D%20FedCFamC1F%20398.rtf`  
  → `Jade Cases/Raw Cases/Pratley & Pratley (No 9) [2026] FedCFamC1F 398.rtf`  
  _url-encoded name_
- `Jade Cases/Raw Cases/Silberman%20&%20Figgins%20%5B2026%5D%20FedCFamC1F%20490.rtf`  
  → `Jade Cases/Raw Cases/Silberman & Figgins [2026] FedCFamC1F 490.rtf`  
  _url-encoded name_
- `Jade Cases/Raw Cases/Sullivan%20&%20Warren%20%5B2026%5D%20FedCFamC1F%20550.rtf`  
  → `Jade Cases/Raw Cases/Sullivan & Warren [2026] FedCFamC1F 550.rtf`  
  _url-encoded name_
- `Jade Cases/Raw Cases/Wilkerson%20&%20Croxford%20%5B2026%5D%20FedCFamC2F%201063.rtf`  
  → `Jade Cases/Raw Cases/Wilkerson & Croxford [2026] FedCFamC2F 1063.rtf`  
  _url-encoded name_

## Filed into a topic folder (26)

- `News Articles/Number of NSW children in youth detention up by one third, new data shows | New South Wales | The Guardian.pdf`  
  → `News Articles/Crime/Number of NSW children in youth detention up by one third, new data shows | New South Wales | The Guardian.pdf`  
  _loose in News Articles/, tagged crime.2_
- `Cases/2012344 (Refugee) [2026] ARTA 2046 (29 April 2026).rtf`  
  → `Cases/Human Rights/2012344 (Refugee) [2026] ARTA 2046 (29 April 2026).rtf`  
  _loose in Cases/, tagged hr.3.1_
- `Cases/2112275(Refugee)%5B2026%5DARTA1503(27March2026).rtf`  
  → `Cases/Human Rights/2112275(Refugee)[2026]ARTA1503(27March2026).rtf`  
  _url-encoded name; loose in Cases/, tagged hr.3.1_
- `Cases/2534313(Refugee)%5B2026%5DARTA1501(16February2026).rtf`  
  → `Cases/Human Rights/2534313(Refugee)[2026]ARTA1501(16February2026).rtf`  
  _url-encoded name; loose in Cases/, tagged hr.3.1_
- `Cases/2540409(Refugee)%5B2025%5DARTA3429(19December2025).rtf`  
  → `Cases/Human Rights/2540409(Refugee)[2025]ARTA3429(19December2025).rtf`  
  _url-encoded name; loose in Cases/, tagged hr.3.1_
- `Cases/Billings and Clowes (No 2) 2026 FedCFamC2F 1367 - Case Summary.pdf`  
  → `Cases/Family/Billings and Clowes (No 2) 2026 FedCFamC2F 1367 - Case Summary.pdf`  
  _loose in Cases/, tagged family_
- `Cases/Billings%20&%20Clowes%20(No%202)%20%5B2026%5D%20FedCFamC2F%201367.rtf`  
  → `Cases/Family/Billings & Clowes (No 2) [2026] FedCFamC2F 1367.rtf`  
  _url-encoded name; loose in Cases/, tagged family_
- `Cases/Brigham and Hibler (Child support) [2026] ARTA 2053 (21 July 2026).rtf`  
  → `Cases/Family/Brigham and Hibler (Child support) [2026] ARTA 2053 (21 July 2026).rtf`  
  _loose in Cases/, tagged fam.1.5_
- `Cases/Cerinza%20&%20Moreau%20%5B2026%5D%20FedCFamC2F%20785.rtf`  
  → `Cases/Family/Cerinza & Moreau [2026] FedCFamC2F 785.rtf`  
  _url-encoded name; loose in Cases/, tagged family_
- `Cases/Coercive Control Worked Example Crime & Family.pdf`  
  → `Cases/Family/Coercive Control Worked Example Crime & Family.pdf`  
  _loose in Cases/, tagged fam.2.4_
- `Cases/Corella & Nagar [2026] FedCFamC2F 1037.rtf`  
  → `Cases/Family/Corella & Nagar [2026] FedCFamC2F 1037.rtf`  
  _loose in Cases/, tagged family_
- `Cases/Curtin & Bush (No 2) [2026] FedCFamC2F 1165.rtf`  
  → `Cases/Family/Curtin & Bush (No 2) [2026] FedCFamC2F 1165.rtf`  
  _loose in Cases/, tagged family_
- `Cases/Curtin & Bush [2026] FedCFamC2F 1021.rtf`  
  → `Cases/Family/Curtin & Bush [2026] FedCFamC2F 1021.rtf`  
  _loose in Cases/, tagged family_
- `Cases/DevineandKitson(Childsupport)%5B2026%5DARTA1944(21July2026).rtf`  
  → `Cases/Family/DevineandKitson(Childsupport)[2026]ARTA1944(21July2026).rtf`  
  _url-encoded name; loose in Cases/, tagged fam.1.5_
- `Cases/Fernley & Masson [2026] FedCFamC2F 958.rtf`  
  → `Cases/Family/Fernley & Masson [2026] FedCFamC2F 958.rtf`  
  _loose in Cases/, tagged family_
- `Cases/GlanceyandGlancey(Childsupport)%5B2026%5DARTA1945(15July2026).rtf`  
  → `Cases/Family/GlanceyandGlancey(Childsupport)[2026]ARTA1945(15July2026).rtf`  
  _url-encoded name; loose in Cases/, tagged fam.1.5_
- `Cases/McAlleyandMinisterforImmigrationandCitizenship(Citizenship)%5B2026%5DARTA1492(3August2026).rtf`  
  → `Cases/Human Rights/McAlleyandMinisterforImmigrationandCitizenship(Citizenship)[2026]ARTA1492(3August2026).rtf`  
  _url-encoded name; loose in Cases/, tagged hr.3.1_
- `Cases/PalgraveandBlackwall(Childsupport)%5B2026%5DARTA1947(15July2026).rtf`  
  → `Cases/Family/PalgraveandBlackwall(Childsupport)[2026]ARTA1947(15July2026).rtf`  
  _url-encoded name; loose in Cases/, tagged fam.1.5_
- `Cases/Plaintiff%20M98-2025%20v%20Minister%20for%20Immigration%20and%20Citizenship%20(M98-2025)%20%5B2026%5D%20HCA%2026.docx`  
  → `Cases/Human Rights/Plaintiff M98-2025 v Minister for Immigration and Citizenship (M98-2025) [2026] HCA 26.docx`  
  _url-encoded name; loose in Cases/, tagged hr.3.1_
- `Cases/RollandandFraser(Childsupport)%5B2025%5DARTA3430(6October2025).rtf`  
  → `Cases/Family/RollandandFraser(Childsupport)[2025]ARTA3430(6October2025).rtf`  
  _url-encoded name; loose in Cases/, tagged fam.1.5_
- `Cases/Swynnerton and Swynnerton (Child support) [2026] ARTA 2033 (15 July 2026).rtf`  
  → `Cases/Family/Swynnerton and Swynnerton (Child support) [2026] ARTA 2033 (15 July 2026).rtf`  
  _loose in Cases/, tagged fam.1.5_
- `Cases/Tanvil & Batta [2026] FedCFamC2F 1001.rtf`  
  → `Cases/Family/Tanvil & Batta [2026] FedCFamC2F 1001.rtf`  
  _loose in Cases/, tagged family_
- `Cases/Three child support reviews - comparison sheet.pdf`  
  → `Cases/Family/Three child support reviews - comparison sheet.pdf`  
  _loose in Cases/, tagged fam.1.5_
- `Cases/Vacek & Novosel (No 7) [2026] FedCFamC2F 1040.rtf`  
  → `Cases/Family/Vacek & Novosel (No 7) [2026] FedCFamC2F 1040.rtf`  
  _loose in Cases/, tagged family_
- `Cases/Walsman%20&%20Walsman%20%5B2026%5D%20FedCFamC2F%20391.rtf`  
  → `Cases/Family/Walsman & Walsman [2026] FedCFamC2F 391.rtf`  
  _url-encoded name; loose in Cases/, tagged family_
- `Cases/Wannell%20&%20Luxford%20%5B2026%5D%20FedCFamC2F%20930.rtf`  
  → `Cases/Family/Wannell & Luxford [2026] FedCFamC2F 930.rtf`  
  _url-encoded name; loose in Cases/, tagged family_

## Duplicates (63)

- `Family/"Enough is enough": NSW child protection system nee... | National Indigenous Times 2.pdf`  
  → `_duplicates/Family/"Enough is enough": NSW child protection system nee... | National Indigenous Times 2.pdf`  
  _a marked copy of Family/"Enough is enough": NSW child protection system nee... | National Indigenous Times.pdf_
- `Family/Childcare crisis: Frankie thought her daughter was safe at daycare but her child’s life changed forever 2.pdf`  
  → `_duplicates/Family/Childcare crisis: Frankie thought her daughter was safe at daycare but her child’s life changed forever 2.pdf`  
  _a marked copy of Family/Childcare crisis: Frankie thought her daughter was safe at daycare but her child’s life changed forever.pdf_
- `Family/Coonabarabran: Children removed from parents before alleged murder 2.pdf`  
  → `_duplicates/Family/Coonabarabran: Children removed from parents before alleged murder 2.pdf`  
  _a marked copy of Family/Coonabarabran: Children removed from parents before alleged murder.pdf_
- `Family/Lunch with Zoe Robinson: The time Mark Latham savaged the NSW advocate for children and young people 2.pdf`  
  → `_duplicates/Family/Lunch with Zoe Robinson: The time Mark Latham savaged the NSW advocate for children and young people 2.pdf`  
  _a marked copy of Family/Lunch with Zoe Robinson: The time Mark Latham savaged the NSW advocate for children and young people.pdf_
- `Family/Melbourne couple’s Colombian IVF surrogacy nightmare | Daily Telegraph.pdf-Phillip Pain MacBook`  
  → `_duplicates/Family/Melbourne couple’s Colombian IVF surrogacy nightmare | Daily Telegraph.pdf-Phillip Pain MacBook`  
  _fixing the name gives Family/Melbourne couple’s Colombian IVF surrogacy nightmare | Daily Telegraph.pdf, which is already there — so this is a copy of it_
- `Family/Nappy wearing dad to launch High Court bid to see his kids | Daily Telegraph.pdf-Phillip Pain MacBook`  
  → `_duplicates/Family/Nappy wearing dad to launch High Court bid to see his kids | Daily Telegraph.pdf-Phillip Pain MacBook`  
  _fixing the name gives Family/Nappy wearing dad to launch High Court bid to see his kids | Daily Telegraph.pdf, which is already there — so this is a copy of it_
- `Family/Postnuptial Agreement In Australia | Justice Family Lawyers.pdf-Phillip Pain MacBook`  
  → `_duplicates/Family/Postnuptial Agreement In Australia | Justice Family Lawyers.pdf-Phillip Pain MacBook`  
  _fixing the name gives Family/Postnuptial Agreement In Australia | Justice Family Lawyers.pdf, which is already there — so this is a copy of it_
- `Family/Re Z Surrogacy arrangements overseas | Law Gazette.pdf-Phillip Pain MacBook`  
  → `_duplicates/Family/Re Z Surrogacy arrangements overseas | Law Gazette.pdf-Phillip Pain MacBook`  
  _fixing the name gives Family/Re Z Surrogacy arrangements overseas | Law Gazette.pdf, which is already there — so this is a copy of it_
- `Family/Single women, same-sex couples to get Medicare rebate for IVF | Herald Sun.pdf-Phillip Pain MacBook`  
  → `_duplicates/Family/Single women, same-sex couples to get Medicare rebate for IVF | Herald Sun.pdf-Phillip Pain MacBook`  
  _fixing the name gives Family/Single women, same-sex couples to get Medicare rebate for IVF | Herald Sun.pdf, which is already there — so this is a copy of it_
- `Family/South Korea adoption: Labor pledges to investigate Australia-Korea program 2.pdf`  
  → `_duplicates/Family/South Korea adoption: Labor pledges to investigate Australia-Korea program 2.pdf`  
  _a marked copy of Family/South Korea adoption: Labor pledges to investigate Australia-Korea program.pdf_
- `Family/Surrogacy Australia: Inquiry examines how government can make path to parenthood easier 2.pdf`  
  → `_duplicates/Family/Surrogacy Australia: Inquiry examines how government can make path to parenthood easier 2.pdf`  
  _a marked copy of Family/Surrogacy Australia: Inquiry examines how government can make path to parenthood easier.pdf_
- `Family/Tracking apps coercive control report: Research by Australian e-safety commissioner shows how apps like Find My Friends, SnapMaps, Life 360 can be abused by killers 2.pdf`  
  → `_duplicates/Family/Tracking apps coercive control report: Research by Australian e-safety commissioner shows how apps like Find My Friends, SnapMaps, Life 360 can be abused by killers 2.pdf`  
  _a marked copy of Family/Tracking apps coercive control report: Research by Australian e-safety commissioner shows how apps like Find My Friends, SnapMaps, Life 360 can be abused by killers.pdf_
- `Family/Tsehay Hawkins: Yellow Wiggle on looking for her birth parents 2.pdf`  
  → `_duplicates/Family/Tsehay Hawkins: Yellow Wiggle on looking for her birth parents 2.pdf`  
  _a marked copy of Family/Tsehay Hawkins: Yellow Wiggle on looking for her birth parents.pdf_
- `Family/Two of Us: Marita and Ashlee McNamara 2.pdf`  
  → `_duplicates/Family/Two of Us: Marita and Ashlee McNamara 2.pdf`  
  _a marked copy of Family/Two of Us: Marita and Ashlee McNamara.pdf_
- `Family/Where public, affordable IVF is available in Australia | Daily Telegraph.pdf-Phillip Pain MacBook`  
  → `_duplicates/Family/Where public, affordable IVF is available in Australia | Daily Telegraph.pdf-Phillip Pain MacBook`  
  _fixing the name gives Family/Where public, affordable IVF is available in Australia | Daily Telegraph.pdf, which is already there — so this is a copy of it_
- `Family/Woman gives birth to stranger’s baby after horror Monash IVF mix-up | Daily Telegraph.pdf-Phillip Pain MacBook`  
  → `_duplicates/Family/Woman gives birth to stranger’s baby after horror Monash IVF mix-up | Daily Telegraph.pdf-Phillip Pain MacBook`  
  _fixing the name gives Family/Woman gives birth to stranger’s baby after horror Monash IVF mix-up | Daily Telegraph.pdf, which is already there — so this is a copy of it_
- `Family/Cases/Khuu & Trang [2026] FedCFamC1F 260.pdf`  
  → `_duplicates/Family/Cases/Khuu & Trang [2026] FedCFamC1F 260.pdf`  
  _same name and format as Cases/Family/Khuu & Trang [2026] FedCFamC1F 260.pdf_
- `Family/Cases/Khuu&Trang_Case_Summary.pdf`  
  → `_duplicates/Family/Cases/Khuu&Trang_Case_Summary.pdf`  
  _same name and format as Cases/Family/Khuu&Trang_Case_Summary.pdf_
- `Family/Cases/Taggart & Gowden [2026] FedCFamC2F 673 (Summary).pdf`  
  → `_duplicates/Family/Cases/Taggart & Gowden [2026] FedCFamC2F 673 (Summary).pdf`  
  _same name and format as Cases/Family/Taggart & Gowden [2026] FedCFamC2F 673 (Summary).pdf_
- `Family/PPT/2023  Surrogacy and Birth Technologies Worksheet(1).docx`  
  → `_duplicates/Family/PPT/2023  Surrogacy and Birth Technologies Worksheet(1).docx`  
  _a marked copy of Family/PPT/2023  Surrogacy and Birth Technologies Worksheet.docx_
- `Family/PPT/2023 PPTX 2. Family - Adoption Rights of Parents(1).pptx`  
  → `_duplicates/Family/PPT/2023 PPTX 2. Family - Adoption Rights of Parents(1).pptx`  
  _a marked copy of Family/PPT/2023 PPTX 2. Family - Adoption Rights of Parents.pptx_
- `Family/PPT/2023 PPTX 4. Legal Rights and Obligations of Parents and Children(1).pptx`  
  → `_duplicates/Family/PPT/2023 PPTX 4. Legal Rights and Obligations of Parents and Children(1).pptx`  
  _a marked copy of Family/PPT/2023 PPTX 4. Legal Rights and Obligations of Parents and Children.pptx_
- `Family/PPT/2026 Set 5 Divorce.pptx`  
  → `_duplicates/Family/PPT/2026 Set 5 Divorce.pptx`  
  _same name and format as Family/PPT/2026 Set 5 - Divorce.pptx_
- `Family/PPT/3c. Surrogacy and Birth Technology- summary.pptx`  
  → `_duplicates/Family/PPT/3c. Surrogacy and Birth Technology- summary.pptx`  
  _same name and format as Family/3c. Surrogacy and Birth Technology- summary.pptx_
- `Family/Evidence Summaries/Care and protection in NSW – what’s new.docx`  
  → `_duplicates/Family/Evidence Summaries/Care and protection in NSW – what’s new.docx`  
  _same name and format as Family/Care and protection in NSW – what’s new.docx_
- `Family/Evidence Summaries/GPS Tracking - Evidence Summary Table.pdf`  
  → `_duplicates/Family/Evidence Summaries/GPS Tracking - Evidence Summary Table.pdf`  
  _same name and format as Family/GPS Tracking - Evidence Summary Table.pdf_
- `News Articles/Family/Tracking Elderly Parents for Safety: How Life360 and GPS Devices Help Caregivers 2.pdf`  
  → `_duplicates/News Articles/Family/Tracking Elderly Parents for Safety: How Life360 and GPS Devices Help Caregivers 2.pdf`  
  _a marked copy of News Articles/Family/Tracking Elderly Parents for Safety: How Life360 and GPS Devices Help Caregivers.pdf_
- `News Articles/Human Rights/Hate speech laws: NSW Labor’s ‘cruel’ new laws do not protect LGBTIQ community 2.pdf`  
  → `_duplicates/News Articles/Human Rights/Hate speech laws: NSW Labor’s ‘cruel’ new laws do not protect LGBTIQ community 2.pdf`  
  _a marked copy of News Articles/Human Rights/Hate speech laws: NSW Labor’s ‘cruel’ new laws do not protect LGBTIQ community.pdf_
- `Cases/Family/Alberdingk_Family_CaseStudy.pdf`  
  → `_duplicates/Cases/Family/Alberdingk_Family_CaseStudy.pdf`  
  _same name and format as Family/Alberdingk_Family_CaseStudy.pdf_
- `Cases/Family/Alberdingk_Family_CaseStudy.pptx`  
  → `_duplicates/Cases/Family/Alberdingk_Family_CaseStudy.pptx`  
  _same name and format as Family/Alberdingk_Family_CaseStudy.pptx_
- `Human Rights/Cases/2111844 (Refugee) [2025] ARTA 3362 Case Summary.pdf`  
  → `_duplicates/Human Rights/Cases/2111844 (Refugee) [2025] ARTA 3362 Case Summary.pdf`  
  _same name and format as Cases/Human Rights/2111844 (Refugee) [2025] ARTA 3362 Case Summary.pdf_
- `Human Rights/Cases/FHST_citizenship_admin_law_summary.pdf`  
  → `_duplicates/Human Rights/Cases/FHST_citizenship_admin_law_summary.pdf`  
  _same name and format as Cases/Human Rights/FHST_citizenship_admin_law_summary.pdf_
- `Human Rights/Cases/Hallmann_v_SCU_human_rights_summary.pdf`  
  → `_duplicates/Human Rights/Cases/Hallmann_v_SCU_human_rights_summary.pdf`  
  _same name and format as Cases/Human Rights/Hallmann_v_SCU_human_rights_summary.pdf_
- `Jade Cases/Raw Cases/2112275(Refugee)%5B2026%5DARTA1503(27March2026).rtf`  
  → `_duplicates/Jade Cases/Raw Cases/2112275(Refugee)%5B2026%5DARTA1503(27March2026).rtf`  
  _same name and format as Cases/2112275(Refugee)%5B2026%5DARTA1503(27March2026).rtf_
- `Jade Cases/Raw Cases/2534313(Refugee)%5B2026%5DARTA1501(16February2026).rtf`  
  → `_duplicates/Jade Cases/Raw Cases/2534313(Refugee)%5B2026%5DARTA1501(16February2026).rtf`  
  _same name and format as Cases/2534313(Refugee)%5B2026%5DARTA1501(16February2026).rtf_
- `Jade Cases/Raw Cases/2540409(Refugee)%5B2025%5DARTA3429(19December2025).rtf`  
  → `_duplicates/Jade Cases/Raw Cases/2540409(Refugee)%5B2025%5DARTA3429(19December2025).rtf`  
  _same name and format as Cases/2540409(Refugee)%5B2025%5DARTA3429(19December2025).rtf_
- `Jade Cases/Raw Cases/Cerinza%20&%20Moreau%20%5B2026%5D%20FedCFamC2F%20785.rtf`  
  → `_duplicates/Jade Cases/Raw Cases/Cerinza%20&%20Moreau%20%5B2026%5D%20FedCFamC2F%20785.rtf`  
  _same name and format as Cases/Cerinza%20&%20Moreau%20%5B2026%5D%20FedCFamC2F%20785.rtf_
- `Jade Cases/Raw Cases/F260100.rtf`  
  → `_duplicates/Jade Cases/Raw Cases/F260100.rtf`  
  _same name and format as Cases/F260100.rtf_
- `Jade Cases/Raw Cases/J261054.rtf`  
  → `_duplicates/Jade Cases/Raw Cases/J261054.rtf`  
  _same name and format as Cases/J261054.rtf_
- `Jade Cases/Raw Cases/J261074.rtf`  
  → `_duplicates/Jade Cases/Raw Cases/J261074.rtf`  
  _same name and format as Cases/J261074.rtf_
- `Jade Cases/Raw Cases/McAlleyandMinisterforImmigrationandCitizenship(Citizenship)%5B2026%5DARTA1492(3August2026).rtf`  
  → `_duplicates/Jade Cases/Raw Cases/McAlleyandMinisterforImmigrationandCitizenship(Citizenship)%5B2026%5DARTA1492(3August2026).rtf`  
  _same name and format as Cases/McAlleyandMinisterforImmigrationandCitizenship(Citizenship)%5B2026%5DARTA1492(3August2026).rtf_
- `Jade Cases/Raw Cases/Plaintiff%20M98-2025%20v%20Minister%20for%20Immigration%20and%20Citizenship%20(M98-2025)%20%5B2026%5D%20HCA%2026.docx`  
  → `_duplicates/Jade Cases/Raw Cases/Plaintiff%20M98-2025%20v%20Minister%20for%20Immigration%20and%20Citizenship%20(M98-2025)%20%5B2026%5D%20HCA%2026.docx`  
  _same name and format as Cases/Plaintiff%20M98-2025%20v%20Minister%20for%20Immigration%20and%20Citizenship%20(M98-2025)%20%5B2026%5D%20HCA%2026.docx_
- `Jade Cases/Raw Cases/RollandandFraser(Childsupport)%5B2025%5DARTA3430(6October2025).rtf`  
  → `_duplicates/Jade Cases/Raw Cases/RollandandFraser(Childsupport)%5B2025%5DARTA3430(6October2025).rtf`  
  _same name and format as Cases/RollandandFraser(Childsupport)%5B2025%5DARTA3430(6October2025).rtf_
- `Jade Cases/Raw Cases/Walsman%20&%20Walsman%20%5B2026%5D%20FedCFamC2F%20391.rtf`  
  → `_duplicates/Jade Cases/Raw Cases/Walsman%20&%20Walsman%20%5B2026%5D%20FedCFamC2F%20391.rtf`  
  _same name and format as Cases/Walsman%20&%20Walsman%20%5B2026%5D%20FedCFamC2F%20391.rtf_
- `Jade Cases/Raw Cases/Wannell%20&%20Luxford%20%5B2026%5D%20FedCFamC2F%20930.rtf`  
  → `_duplicates/Jade Cases/Raw Cases/Wannell%20&%20Luxford%20%5B2026%5D%20FedCFamC2F%20930.rtf`  
  _same name and format as Cases/Wannell%20&%20Luxford%20%5B2026%5D%20FedCFamC2F%20930.rtf_
- `Jade Cases/Completed Case Summaries/01_Cerinza_and_Moreau_2026_FedCFamC2F_785.pdf`  
  → `_duplicates/Jade Cases/Completed Case Summaries/01_Cerinza_and_Moreau_2026_FedCFamC2F_785.pdf`  
  _same name and format as Cases/Family/01_Cerinza_and_Moreau_2026_FedCFamC2F_785.pdf_
- `Jade Cases/Completed Case Summaries/12_Metropolitan_LALC_4_v_Attorney_General_NSW_2026_FCA_1074.pdf`  
  → `_duplicates/Jade Cases/Completed Case Summaries/12_Metropolitan_LALC_4_v_Attorney_General_NSW_2026_FCA_1074.pdf`  
  _same name and format as Cases/Shelter/12_Metropolitan_LALC_4_v_Attorney_General_NSW_2026_FCA_1074.pdf_
- `Jade Cases/Completed Case Summaries/2535647_Refugee_ARTA1395_Case_Study_Card.pdf`  
  → `_duplicates/Jade Cases/Completed Case Summaries/2535647_Refugee_ARTA1395_Case_Study_Card.pdf`  
  _same name and format as Cases/Human Rights/2535647_Refugee_ARTA1395_Case_Study_Card.pdf_
- `Jade Cases/Completed Case Summaries/One birth, two pregnancies, two sets of parents.pdf`  
  → `_duplicates/Jade Cases/Completed Case Summaries/One birth, two pregnancies, two sets of parents.pdf`  
  _same name and format as Cases/Family/One birth, two pregnancies, two sets of parents.pdf_
- `Jade Cases/Completed Case Summaries/Three child support reviews - comparison sheet.pdf`  
  → `_duplicates/Jade Cases/Completed Case Summaries/Three child support reviews - comparison sheet.pdf`  
  _same name and format as Cases/Three child support reviews - comparison sheet.pdf_
- `Shelter/Australia housing crisis: Planned 100,000 new homes in NSW still not delivered 14 months later 2.pdf`  
  → `_duplicates/Shelter/Australia housing crisis: Planned 100,000 new homes in NSW still not delivered 14 months later 2.pdf`  
  _a marked copy of Shelter/Australia housing crisis: Planned 100,000 new homes in NSW still not delivered 14 months later.pdf_
- `Shelter/First Home Guarantee scheme - Sydney property: Help to Buy first home buyer scheme to offer buyers a choice 2.pdf`  
  → `_duplicates/Shelter/First Home Guarantee scheme - Sydney property: Help to Buy first home buyer scheme to offer buyers a choice 2.pdf`  
  _a marked copy of Shelter/First Home Guarantee scheme - Sydney property: Help to Buy first home buyer scheme to offer buyers a choice.pdf_
- `Shelter/NSW rental laws What are the changes?.pdf-Phillip Pain MacBook`  
  → `_duplicates/Shelter/NSW rental laws What are the changes?.pdf-Phillip Pain MacBook`  
  _fixing the name gives Shelter/NSW rental laws What are the changes?.pdf, which is already there — so this is a copy of it_
- `Shelter/Shoddy Sydney: Home defects crisis collides with the need to build housing 2.pdf`  
  → `_duplicates/Shelter/Shoddy Sydney: Home defects crisis collides with the need to build housing 2.pdf`  
  _a marked copy of Shelter/Shoddy Sydney: Home defects crisis collides with the need to build housing.pdf_
- `Shelter/Sydney’s building defects cost $700m a year, but what is being done to fix the problem?.pdf-Phillip Pain MacBook`  
  → `_duplicates/Shelter/Sydney’s building defects cost $700m a year, but what is being done to fix the problem?.pdf-Phillip Pain MacBook`  
  _fixing the name gives Shelter/Sydney’s building defects cost $700m a year, but what is being done to fix the problem?.pdf, which is already there — so this is a copy of it_
- `Shelter/Shelter Videos/Container Homes.MP4`  
  → `_duplicates/Shelter/Shelter Videos/Container Homes.MP4`  
  _same name and format as Shelter/Container Homes.mp4_
- `Shelter/Shelter PowerPoints/Shelter PPT 12LEG1.pdf`  
  → `_duplicates/Shelter/Shelter PowerPoints/Shelter PPT 12LEG1.pdf`  
  _same name and format as Shelter/Shelter PPT 12LEG1.pdf_
- `Shelter/Shelter PowerPoints/~$1a. Nature of Shelter - Intro.pptx`  
  → `_duplicates/Shelter/Shelter PowerPoints/~$1a. Nature of Shelter - Intro.pptx`  
  _same name and format as Shelter/Shelter PowerPoints/1a. Nature of Shelter - Intro.pptx_
- `Crime/International Crime/12LS International Crime.pptx`  
  → `_duplicates/Crime/International Crime/12LS International Crime.pptx`  
  _same name and format as International Crime/12LS International Crime.pptx_
- `Crime/Sentencing and Punishment/Cheat Sheet Juries.pdf`  
  → `_duplicates/Crime/Sentencing and Punishment/Cheat Sheet Juries.pdf`  
  _same name and format as Crime/Criminal Trial Process/Cheat Sheet Juries.pdf_
- `Crime/Media/Australia slavery: Woman forced into sexual servitude advising anti-slavery commissioner 2.pdf`  
  → `_duplicates/Crime/Media/Australia slavery: Woman forced into sexual servitude advising anti-slavery commissioner 2.pdf`  
  _a marked copy of Crime/Media/Australia slavery: Woman forced into sexual servitude advising anti-slavery commissioner.pdf_
- `Tiktok Videos/Erin_Patterson_Forest 2.MP4`  
  → `_duplicates/Tiktok Videos/Erin_Patterson_Forest 2.MP4`  
  _a marked copy of Tiktok Videos/Erin_Patterson_Forest.MP4_
- `Tiktok Videos/v14044g50000d1n0d1nog65i1mc133k0 2.MP4`  
  → `_duplicates/Tiktok Videos/v14044g50000d1n0d1nog65i1mc133k0 2.MP4`  
  _a marked copy of Tiktok Videos/v14044g50000d1n0d1nog65i1mc133k0.MP4_

## Not Legal Studies (1)

- `Family/11Eco6 2025 Pain Task 2.docx`  
  → `_not-legal-studies/11Eco6 2025 Pain Task 2.docx`  
  _does not look like Legal Studies_
