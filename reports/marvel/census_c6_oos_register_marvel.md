# C6 OOS freeze register (marvel, pre-model-call)

Frozen before the C6 GPU window's first model call. Re-grade set = the census
re-run (whole per-class draw) + the 200 OOS rows below. The OOS is the
anti-theater arm: the executing agent runs it and never edits it.

## Rule
- Seed: 20260927 (one `random.Random` instance: the per-class census draws in
  sorted class order first, then the OOS draw over the remaining pool, all
  over id-sorted candidates — the JJK D6 chair-lock shape)
- Population: the whole C6 bank (`census_c6_bank_marvel.jsonl`, 1041787 rows
  over 99581 swept pages; census + OOS combined)
- Draws are over the WHOLE population (chair lock): no leak exclusion. Rows on
  pages the later prose work improves stay in the pool — the closure test is a
  score floor (post >= pre - 2, a drop of 3+ voids, CSM annex), so they can
  only rise, never trip the floor
- Disjointness: census draw ∩ OOS = ∅ (asserted at build) — the OOS is a
  holdout; the census draw is the re-run arm and may not leak into it
- Census draw: {'affiliation': 10, 'alias': 4, 'aliases': 10, 'currentalias': 10, 'identity': 10, 'nicknames': 10, 'spouses': 10} rows (per-class 10,
  the JJK 14x10 shape), classes = affiliation, alias, aliases, currentalias, identity, nicknames, spouses
- OOS: 200 rows drawn from (population - census draw), pool
  1041723 rows

## Counts
- OOS class mix: {"affiliation": 2, "aliases": 3, "currentalias": 11, "identity": 183, "spouses": 1}
- bank per-class: {"affiliation": 21334, "alias": 4, "aliases": 13622, "currentalias": 55095, "identity": 945001, "nicknames": 2287, "spouses": 4444}
- sweep state at freeze: 99591 pages,
  0 errors (complete=True)

## Pre-scoring method (recorded for the pre-baseline)
In-process qa door (`build_context(paths, q, mode="qa", subject=None)` +
`span_recall.served_text` — the same path the `:8000` `/context` endpoint
uses), device `cuda` (GPU-only), judged by
`tools.census_dimensions.judge` (the 2/3 rule: a bank of 3 expect terms
needs >= 2, variable-length banks scale to ceil(2n/3); MECH_GREEN).

## OOS ids
- marvel-pg-benedicto_de_vica_severtes_earth_616-007
- marvel-pg-john_c_wilson_earth_616-001
- marvel-pg-nakia_bahadir_earth_199999-012
- marvel-pg-ricardo_dominguez_earth_616-004
- marvel-pg-amatsu_mikaboshi_earth_616-018
- marvel-pg-nicholas_fury_earth_200506-007
- marvel-pg-gary_tan_earth_616-004
- marvel-pg-augur_earth_148611-006
- marvel-pg-dana_bradley_earth_93060-004
- marvel-pg-vola_earth_616-006
- marvel-pg-sico_rudo_earth_616-009
- marvel-pg-jonathan_walker_earth_93342-003
- marvel-pg-martu_earth_616-011
- marvel-pg-loki_laufeyson_earth_89768-006
- marvel-pg-uatu_earth_77119-012
- marvel-pg-bonesaw_mcgraw_earth_11714-001
- marvel-pg-alexander_power_earth_91119-005
- marvel-pg-larry_marsden_earth_616-005
- marvel-pg-robert_frank_jr_earth_616-003
- marvel-pg-dar_benn_earth_199999-003
- marvel-pg-william_gant_earth_616-009
- marvel-pg-eden_fesi_earth_59512-003
- marvel-pg-karl_lykos_earth_295-015
- marvel-pg-namor_earth_421-008
- marvel-pg-kargus_earth_616-012
- marvel-pg-venom_symbiote_earth_12101-003
- marvel-pg-eva_bell_moira_vii_1-008
- marvel-pg-stephen_strange_earth_81223-002
- marvel-pg-peter_parker_jubilee_10-007
- marvel-pg-diego_casseas_earth_616-008
- marvel-pg-pietro_maximoff_earth_295-004
- marvel-pg-conobar_earth_616-003
- marvel-pg-heinrich_von_schnickelschnapp_earth_616-004
- marvel-pg-max_eisenhardt_earth_78909-010
- marvel-pg-tim_boo_ba_earth_616-012
- marvel-pg-rogue_anna_marie_earth_7964-007
- marvel-pg-zebedee_rcx_earth_616-002
- marvel-pg-peter_scioli_earth_616-006
- marvel-pg-carrie_earth_616-010
- marvel-pg-wanda_maximoff_earth_9916-010
- marvel-pg-barbara_robb_earth_616-016
- marvel-pg-sergei_kravinoff_earth_42155-003
- marvel-pg-bobb_earth_9500-003
- marvel-pg-gwen_kasper_s_fianc_earth_616-011
- marvel-pg-john_jonah_jameson_iii_earth_trn566-006
- marvel-pg-ivan_vanko_whiplash_earth_199999-004
- marvel-pg-gordon_phillips_earth_616-014
- marvel-pg-robert_baldwin_earth_45561-007
- marvel-pg-monica_rambeau_earth_22795-011
- marvel-pg-johnny_carson_earth_616-004
- marvel-pg-ava_ayala_earth_12041-012
- marvel-pg-kevin_albers_earth_93060-002
- marvel-pg-sanara_earth_616-012
- marvel-pg-thor_odinson_earth_19411-002
- marvel-pg-shanna_o_hara_earth_11911-009
- marvel-pg-agent_colt_earth_616-004
- marvel-pg-uatu_earth_20824-002
- marvel-pg-brandon_kay_earth_21127-003
- marvel-pg-phillip_coulson_earth_13122-006
- marvel-pg-philip_sterns_earth_616-010
- marvel-pg-natasha_romanova_earth_101001-010
- marvel-pg-jean_grey_earth_21376-007
- marvel-pg-raven_darkh_lme_earth_93342-001
- marvel-pg-rita_wayward_jubilee_10-001
- marvel-pg-vincent_patilio_earth_trn1526-005
- marvel-pg-klug_earth_616-002
- marvel-pg-jeanne_marie_beaubier_earth_20051-002
- marvel-pg-gilberto_coraz_n_earth_41940-006
- marvel-pg-ilsa_moon_earth_616-001
- marvel-pg-ivan_kragoff_earth_700089-003
- marvel-pg-tabicantra_earth_616-010
- marvel-pg-paul_domenic_earth_616-006
- marvel-pg-madelyne_pryor_earth_616-005
- marvel-pg-stephen_strange_earth_trn1121-004
- marvel-pg-urd_earth_46266-002
- marvel-pg-piotr_rasputin_earth_90816-012
- marvel-pg-maxwell_dillon_earth_17154-007
- marvel-pg-teresia_karisik_earth_17372-008
- marvel-pg-dwayne_taylor_earth_18119-011
- marvel-pg-william_baker_earth_trn1145-005
- marvel-pg-james_howlett_earth_trn1286-007
- marvel-pg-lou_bazo_jr_earth_616-002
- marvel-pg-crystalia_amaquelin_earth_2149-011
- marvel-pg-rico_estevez_earth_928-005
- marvel-pg-susan_storm_earth_92131-006
- marvel-pg-beta_ray_bill_earth_trn996-005
- marvel-pg-jonathan_storm_earth_94561-009
- marvel-pg-professor_fear_earth_616-002
- marvel-pg-hex_butcher_earth_616-014
- marvel-pg-john_rost_earth_148611-006
- marvel-pg-bullseye_lester_earth_517-009
- marvel-pg-arlo_cordco_earth_616-005
- marvel-pg-henry_pym_earth_9602-005
- marvel-pg-mig_el_gand_earth_9602-008
- marvel-pg-n_kki_earth_616-004
- marvel-pg-mariko_yashida_earth_989192-004
- marvel-pg-stupor_earth_691-011
- marvel-pg-thaddeus_ross_earth_8222-001
- marvel-pg-amanda_payne_earth_616-001
- marvel-pg-francis_castle_earth_trn666-004
- marvel-pg-irving_forbush_earth_616-003
- marvel-pg-amadeus_cho_earth_23203-005
- marvel-pg-james_howlett_earth_10071-004
- marvel-pg-skunk_ape_earth_616-012
- marvel-pg-kronus_wilkins_earth_616-007
- marvel-pg-marco_reporter_earth_616-001
- marvel-pg-rocket_earth_trn971-004
- marvel-pg-james_howlett_earth_6160-007
- marvel-pg-nathaniel_essex_earth_1610-012
- marvel-pg-peter_porker_earth_8311-002
- marvel-pg-jim_hammond_earth_9200-004
- marvel-pg-peter_parker_supreme_earth_517-003
- marvel-pg-jonathan_clark_earth_616-013
- marvel-pg-lucas_cage_earth_6025-003
- marvel-pg-henry_pym_earth_8110-005
- marvel-pg-finch_daily_bugle_earth_616-004
- marvel-pg-james_howlett_earth_8441-002
- marvel-pg-steven_rogers_earth_374-008
- marvel-pg-dervish_the_arena_earth_616-004
- marvel-pg-kantu_mute_zoner_earth_616-005
- marvel-pg-dimitri_bukharin_earth_13122-003
- marvel-pg-richard_parker_earth_70105-003
- marvel-pg-orion_earth_9602-005
- marvel-pg-jody_putt_earth_616-017
- marvel-pg-adolphus_earth_616-002
- marvel-pg-jasmine_hyboria_earth_616-012
- marvel-pg-ella_sterling_earth_616-003
- marvel-pg-callix_earth_616-007
- marvel-pg-lucia_von_bardas_earth_trn1407-007
- marvel-pg-emma_frost_earth_928-009
- marvel-pg-frederick_myers_earth_12041-005
- marvel-pg-adoro_earth_17995-011
- marvel-pg-karl_malus_earth_199999-005
- marvel-pg-miklho_earth_11080-002
- marvel-pg-victor_creed_earth_trn1423-003
- marvel-pg-miss_locke_android_earth_616-005
- marvel-pg-vashti_cleito_son_earth_616-005
- marvel-pg-otto_octavius_earth_18119-013
- marvel-pg-elaine_grey_earth_161-005
- marvel-pg-patricia_hamilton_earth_616-004
- marvel-pg-kurt_wagner_earth_28918-008
- marvel-pg-chad_channing_earth_2992-008
- marvel-pg-mark_hoeppner_earth_616-012
- marvel-pg-theodore_altman_earth_24110-007
- marvel-pg-nance_winters_earth_616-003
- marvel-pg-jen_gaines_earth_616-012
- marvel-pg-hapless_hogun_earth_665-001
- marvel-pg-victor_von_doom_earth_2099-014
- marvel-pg-tyrone_johnson_earth_22145-005
- marvel-pg-sam_striker_earth_616-011
- marvel-pg-magilla_grod_earth_9047-001
- marvel-pg-charles_xavier_earth_81727-014
- marvel-pg-carnage_symbiote_earth_trn1800-011
- marvel-pg-neilsen_earth_9047-010
- marvel-pg-simon_bray_earth_616-010
- marvel-pg-kyle_brock_earth_616-010
- marvel-pg-norah_winters_earth_616-001
- marvel-pg-samuel_wilson_earth_9021-003
- marvel-pg-henry_pym_earth_617-003
- marvel-pg-nick_manolis_earth_555-007
- marvel-pg-antimatter_earth_616-008
- marvel-pg-varanus_earth_616-010
- marvel-pg-edwin_jarvis_earth_10208-005
- marvel-pg-super_adaptoid_earth_807128-013
- marvel-pg-bonita_juarez_earth_81147-007
- marvel-pg-brutus_klor_earth_616-001
- marvel-pg-stephen_strange_earth_12041-004
- marvel-pg-otto_octavius_earth_14702-010
- marvel-pg-annihilus_earth_trn666-010
- marvel-pg-ape_morlock_earth_50302-005
- marvel-pg-dennis_lawrence_earth_85101-009
- marvel-pg-christopher_powell_earth_2992-003
- marvel-pg-eleanor_blackwood_earth_616-004
- marvel-pg-molossus_earth_88131-011
- marvel-pg-remy_lebeau_earth_961116-003
- marvel-pg-woody_banner_earth_807128-004
- marvel-pg-hollowpoint_ninja_earth_616-008
- marvel-pg-marcia_kenwell_earth_616-002
- marvel-pg-iron_man_sentient_armor_earth_616-002
- marvel-pg-joseph_mitchell_earth_616-013
- marvel-pg-charles_weiderman_earth_616-014
- marvel-pg-kondrati_topolov_earth_58163-006
- marvel-pg-bonebreaker_earth_1610-007
- marvel-pg-erik_the_red_earth_32000-004
- marvel-pg-katherine_beere_earth_616-006
- marvel-pg-omega_black_earth_47301-001
- marvel-pg-solon_stabilizer_earth_616-004
- marvel-pg-martin_li_impostor_earth_96835-008
- marvel-pg-bulwar_earth_616-002
- marvel-pg-ultron_v_onslaught_reborn_earth_616-007
- marvel-pg-nick_rodriguez_earth_616-014
- marvel-pg-manuel_fokus_earth_928-008
- marvel-pg-eileen_barnes_earth_616-002
- marvel-pg-mikon_earth_616-001
- marvel-pg-elizabeth_braddock_earth_2301-010
- marvel-pg-schuyler_belial_earth_616-003
- marvel-pg-spencer_breen_earth_616-005
- marvel-pg-jean_grey_earth_19345-005
- marvel-pg-james_buchanan_barnes_earth_43225-003
- marvel-pg-anton_aubuisson_earth_616-006
