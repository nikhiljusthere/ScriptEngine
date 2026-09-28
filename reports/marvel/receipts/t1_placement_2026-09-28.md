# T1 placement receipts — 2026-09-28 (story_arc re-run + 2 mcu budget retries)

Chain `/tmp/opencode/c4_t1_rerun.sh`, log `/tmp/opencode/c4_t1_rerun.log`:
START 08:17:57, both phases rc=0, `T1 RE-RUN CHAIN DONE` 08:42:02. failed=0
in both runs.

## Run 1 — marvel placement re-run (08:17:57 – 08:36:26, rc=0)

| outcome | count |
|---|---:|
| considered | 213 |
| extracted | 98 |
| cached | 115 |
| failed | 0 |
| new events | 72 |

Queue = 115 cached (read under the current prompt + revid in the 06:14 run)
+ 98 extracted (15 new `story_arc` pages + 83 previously-read zero-event
pages). Cache state note: `save_events` is DELETE + INSERT with no state
marker for an empty arc, so a page that read to 0 events stores no
`events` rows and is never a cache hit — it is re-read on every run. The 83
re-reads are this behaviour, not a regression.

Post-run store: **1,221 events; 79 on the time axis** (1,142 standing).
Pre-R3 alignment; the store time axis (design §3) re-derives `temporal`
without a re-extraction.

## Run 2 — mcu budget retries (08:36:26 – 08:42:02, rc=0, ANSWER_TOKENS=20480)

The 2 pages that failed the 06:14 run on the answer-token budget:
`Battle of Wakanda` — "used its whole token budget on reasoning and
never answered"; `Infiltration into Westview` — "hit max_tokens (8192)
mid-answer, so the reply is truncated and cannot be parsed".

| page | events |
|---|---:|
| Battle of Wakanda | 43 |
| Infiltration into Westview | 12 |

considered 2 · extracted 2 · cached 0 · **failed 0** · 55 events. The mcu
side reaches failed=0: no remaining failed page to name.

Post-run store: **6,108 events; 0 on the time axis** (the mcu axis signals
land with R3/T2b; design §3).

## 0-event page account

### marvel — 85 of 213 (every one read this run, every one 0 retained)

All 85 carry ≥1 extractable section; "0 retained" means the section prose
states no event naming two of the wiki's resolved participants, or every
candidate row failed a gate (unknown participant / unverbatim quote /
off-axis). Word counts are stripped prose over the page's extractable
sections.

| page | extractable sections | words (stripped) | account |
|---|---:|---:|---|
| Pre-Cataclysmic Age | 14 | 1089 | read this run, 0 retained |
| Hyborian Age | 9 | 1010 | read this run, 0 retained |
| Spider-Verse | 2 | 944 | read this run, 0 retained |
| Great Cataclysm | 6 | 905 | read this run, 0 retained |
| Vietnam War | 4 | 857 | read this run, 0 retained |
| A.X.E.: Judgment Day | 2 | 733 | read this run, 0 retained |
| Olympic Games | 6 | 726 | read this run, 0 retained |
| Siege of the City of Wonders | 3 | 686 | read this run, 0 retained |
| Wraith-Galadorian War | 4 | 528 | read this run, 0 retained |
| Heroes Reborn (2021 Event) | 2 | 523 | read this run, 0 retained |
| French Revolution | 4 | 498 | read this run, 0 retained |
| Celestial War | 3 | 458 | read this run, 0 retained |
| Titanomachy | 2 | 450 | read this run, 0 retained |
| Black Plague (Event) | 6 | 410 | read this run, 0 retained |
| Heroes Reborn (1996 Event) | 2 | 401 | read this run, 0 retained |
| Thousand Year War | 6 | 396 | read this run, 0 retained |
| 1906 San Francisco Earthquake | 4 | 372 | read this run, 0 retained |
| Watergate Scandal | 3 | 325 | read this run, 0 retained |
| Civil War II | 2 | 324 | read this run, 0 retained |
| Russian Revolution | 2 | 321 | read this run, 0 retained |
| Final Battle with the Elder Gods | 3 | 309 | read this run, 0 retained |
| Gulf War | 4 | 297 | read this run, 0 retained |
| Iraq War | 2 | 290 | read this run, 0 retained |
| Roswell UFO Incident | 2 | 271 | read this run, 0 retained |
| Post-Hyborian Cataclysm | 2 | 260 | read this run, 0 retained |
| English Civil War | 3 | 259 | read this run, 0 retained |
| Iron Man 2020 (Event) | 1 | 234 | read this run, 0 retained |
| Cretaceous–Paleogene Extinction Event | 1 | 226 | read this run, 0 retained |
| Soviet-Afghan War | 2 | 220 | read this run, 0 retained |
| Infinite Destinies | 1 | 210 | read this run, 0 retained |
| Spanish-American War | 3 | 200 | read this run, 0 retained |
| Outlawed | 2 | 189 | read this run, 0 retained |
| Cuban Missile Crisis | 5 | 181 | read this run, 0 retained |
| Seven Years' War | 3 | 181 | read this run, 0 retained |
| Blood Hunt | 2 | 180 | read this run, 0 retained |
| Necrosha | 1 | 180 | read this run, 0 retained |
| Chernobyl Disaster | 3 | 174 | read this run, 0 retained |
| Infinity Gauntlet (Event) | 1 | 155 | read this run, 0 retained |
| Evolutionary War | 1 | 152 | read this run, 0 retained |
| Marvel NOW! (2012 Event) | 1 | 145 | read this run, 0 retained |
| Acts of Vengeance (Event) | 1 | 140 | read this run, 0 retained |
| Heaven's on Fire | 2 | 138 | read this run, 0 retained |
| Monsters Unleashed (Event) | 1 | 132 | read this run, 0 retained |
| Utopia (Event) | 1 | 129 | read this run, 0 retained |
| Time Runs Out | 1 | 128 | read this run, 0 retained |
| Second Coming | 3 | 124 | read this run, 0 retained |
| Galactic Marathon | 1 | 123 | read this run, 0 retained |
| Human-Deviant Wars | 2 | 122 | read this run, 0 retained |
| One World Under Doom | 1 | 118 | read this run, 0 retained |
| All-New Marvel NOW! | 1 | 115 | read this run, 0 retained |
| Avengers Disassembled | 1 | 112 | read this run, 0 retained |
| Clinton–Lewinsky Scandal | 2 | 106 | read this run, 0 retained |
| U-Decide! | 1 | 102 | read this run, 0 retained |
| Avengers/JLA | 1 | 99 | read this run, 0 retained |
| Muir Island Saga | 1 | 99 | read this run, 0 retained |
| Venom War (Event) | 1 | 98 | read this run, 0 retained |
| Lesser Cataclysm | 3 | 96 | read this run, 0 retained |
| Infinity Wars | 2 | 86 | read this run, 0 retained |
| Cataclysm | 1 | 83 | read this run, 0 retained |
| Black September | 2 | 82 | read this run, 0 retained |
| Secret Empire (Event) | 1 | 82 | read this run, 0 retained |
| End Times | 1 | 80 | read this run, 0 retained |
| Battle of the Atom | 2 | 78 | read this run, 0 retained |
| Eve of Destruction | 1 | 76 | read this run, 0 retained |
| Captain America: Cold War | 1 | 72 | read this run, 0 retained |
| Fear Itself | 1 | 70 | read this run, 0 retained |
| X-Manhunt | 1 | 70 | read this run, 0 retained |
| Avengers NOW! | 1 | 66 | read this run, 0 retained |
| First Great War of the Gods | 1 | 56 | read this run, 0 retained |
| Go Down Swinging | 1 | 51 | read this run, 0 retained |
| All-New, All-Different Marvel | 1 | 40 | read this run, 0 retained |
| Heroic Age (Event) | 1 | 37 | read this run, 0 retained |
| Bad New Day | 1 | 37 | read this run, 0 retained |
| Super Olympics | 1 | 34 | read this run, 0 retained |
| Infinity Countdown | 1 | 32 | read this run, 0 retained |
| Regenesis | 1 | 32 | read this run, 0 retained |
| Ultimate Marvel NOW! | 1 | 30 | read this run, 0 retained |
| ResurrXion | 1 | 29 | read this run, 0 retained |
| Sins of Sinister | 1 | 29 | read this run, 0 retained |
| Devil's Reign (2022 Event) | 1 | 28 | read this run, 0 retained |
| Gang War (Event) | 1 | 28 | read this run, 0 retained |
| Forty-Third Troll War | 1 | 27 | read this run, 0 retained |
| Magneto War | 1 | 27 | read this run, 0 retained |
| Dawn of X | 1 | 26 | read this run, 0 retained |
| Guardians of the Galaxy & X-Men: Black Vortex | 1 | 25 | read this run, 0 retained |

### mcu — 150 of 1,323 (0 unread queue tail · 150 read-0)

The 06:14 run considered the full 1,323-page queue (1,321 extracted · 2
failed · 6,053 events); the retries extracted both failures, so every
placement page has been read and the queue tail is empty. All 150
zero-event pages are read-0 — their prose states no event naming two
resolved participants, or every candidate row failed a gate (same
account as the marvel set above). Log note: five long slash-titled pages
print truncated at the console width in the 06:14 log; their event
counts are the store's.

| page | extractable sections | words (stripped) | account |
|---|---:|---:|---|
| Battle on the Maribel del Mar | 3 | 1217 | read 06:14 run, 0 retained |
| Bombing of Hell's Kitchen | 3 | 1024 | read 06:14 run, 0 retained |
| Murder of Daniel Blake | 3 | 987 | read 06:14 run, 0 retained |
| Assassination of Christofi Savva | 3 | 905 | read 06:14 run, 0 retained |
| Search for Ammit's Ushabti | 3 | 879 | read 06:14 run, 0 retained |
| Kidnapping of Jeffrey Mace | 5 | 871 | read 06:14 run, 0 retained |
| Ambush on the FBI Convoy | 3 | 800 | read 06:14 run, 0 retained |
| Hijacking and Retaking of the Lemurian Star | 5 | 798 | read 06:14 run, 0 retained |
| Kidnapping of Kevin Bacon | 3 | 783 | read 06:14 run, 0 retained |
| Battle on the Iliad | 3 | 782 | read 06:14 run, 0 retained |
| Destruction of the O.X.E. Kuala Lumpur Research Facility | 3 | 724 | read 06:14 run, 0 retained |
| Battle of Celestial Island | 3 | 691 | read 06:14 run, 0 retained |
| Attack on the Cage-Jones Residence | 3 | 657 | read 06:14 run, 0 retained |
| Big Bang | 5 | 649 | read 06:14 run, 0 retained |
| Battle at Josie's Bar | 3 | 637 | read 06:14 run, 0 retained |
| Duel at Lion's Kingdom | 3 | 630 | read 06:14 run, 0 retained |
| Attack on Agnes O'Connor's House | 3 | 628 | read 06:14 run, 0 retained |
| New Jersey AvengerCon | 3 | 627 | read 06:14 run, 0 retained |
| Ambush in Kandahar | 3 | 624 | read 06:14 run, 0 retained |
| Arrest of Leroy Bradford | 3 | 623 | read 06:14 run, 0 retained |
| Ambush in Mesopotamia | 3 | 610 | read 06:14 run, 0 retained |
| Attack on the Maggia Weapons Caches/A.I.M. Operative Controller | 3 | 603 | read 06:14 run, 0 retained |
| Ambush in Micro's Hideout | 3 | 590 | read 06:14 run, 0 retained |
| Defense of the Lighthouse | 3 | 588 | read 06:14 run, 0 retained |
| Siege of the Hydra Broadcasting Center | 3 | 586 | read 06:14 run, 0 retained |
| Robbery of the Queens Community Bank | 4 | 585 | read 06:14 run, 0 retained |
| Theft of the Time Stone | 3 | 585 | read 06:14 run, 0 retained |
| Assassination of Gene and Alice Hernandez | 3 | 572 | read 06:14 run, 0 retained |
| Kidnapping of Charles Hinton | 3 | 570 | read 06:14 run, 0 retained |
| Ambush on Glenn Talbot | 3 | 566 | read 06:14 run, 0 retained |
| Capture of Dottie Underwood | 3 | 564 | read 06:14 run, 0 retained |
| Kidnapping of New Orleans Gang Leaders | 3 | 539 | read 06:14 run, 0 retained |
| Ambush at the Grand Central Terminal | 3 | 536 | read 06:14 run, 0 retained |
| Theft of the Dataspine | 3 | 522 | read 06:14 run, 0 retained |
| Attack on Manhattan | 2 | 508 | read 06:14 run, 0 retained |
| Ambush at the Barbershop Headquarters | 3 | 503 | read 06:14 run, 0 retained |
| Rum Punch Massacre | 3 | 492 | read 06:14 run, 0 retained |
| Robbery of the Roxxon Gas Station | 3 | 488 | read 06:14 run, 0 retained |
| Attack on the Lighthouse | 3 | 487 | read 06:14 run, 0 retained |
| Escape from the Sovereign Fleet | 4 | 485 | read 06:14 run, 0 retained |
| Robbery of VistaCorp | 3 | 485 | read 06:14 run, 0 retained |
| Attack on Sam Wilson | 3 | 479 | read 06:14 run, 0 retained |
| Escape from S.H.I.E.L.D. | 3 | 479 | read 06:14 run, 0 retained |
| Attack on Peter Quill | 3 | 478 | read 06:14 run, 0 retained |
| Capture of Trok | 3 | 474 | read 06:14 run, 0 retained |
| Ambush on Peter Scarborough | 3 | 471 | read 06:14 run, 0 retained |
| Assassination of Hydra Leaders | 3 | 463 | read 06:14 run, 0 retained |
| Coup for Asgard's Throne | 3 | 463 | read 06:14 run, 0 retained |
| Kidnapping of Franklin Hall | 3 | 457 | read 06:14 run, 0 retained |
| Arrest of the Albanian Syndicate | 3 | 448 | read 06:14 run, 0 retained |
| Arrest of Peter Parker | 3 | 445 | read 06:14 run, 0 retained |
| Infiltration into the MacArthur Grand Hotel | 3 | 442 | read 06:14 run, 0 retained |
| Attack on Luke Cage Heroin Warehouse | 3 | 432 | read 06:14 run, 0 retained |
| Infiltration into J.A.R.V.I.S.' Systems | 3 | 432 | read 06:14 run, 0 retained |
| Infiltration into Ellen Nadeer's Office | 3 | 430 | read 06:14 run, 0 retained |
| Liberation of Agatha Harkness | 3 | 428 | read 06:14 run, 0 retained |
| Capture of Loki | 3 | 423 | read 06:14 run, 0 retained |
| Attack in Norway/Super Soldier Peggy Carter | 3 | 422 | read 06:14 run, 0 retained |
| Jones Family Car Crash | 4 | 419 | read 06:14 run, 0 retained |
| Attack on the Al-Kut Air Base | 3 | 418 | read 06:14 run, 0 retained |
| Rescue in Bahrain/Framework | 3 | 415 | read 06:14 run, 0 retained |
| Massacre at the Cinema Theater | 3 | 399 | read 06:14 run, 0 retained |
| Robbery of Gasel Bank | 3 | 399 | read 06:14 run, 0 retained |
| Raid of Khonshu's Temple | 3 | 397 | read 06:14 run, 0 retained |
| Captain America's USO Show | 2 | 396 | read 06:14 run, 0 retained |
| Celestial Island World Summit | 3 | 394 | read 06:14 run, 0 retained |
| Arrest of Benjamin Pollack and Claire Weiss | 3 | 390 | read 06:14 run, 0 retained |
| Arrest of New York City's Crime Bosses | 3 | 388 | read 06:14 run, 0 retained |
| Arrest of Liam Walsh | 3 | 383 | read 06:14 run, 0 retained |
| Hijacking and Retaking of the Prototype Destroyer | 4 | 382 | read 06:14 run, 0 retained |
| Attack on the Harvey Sub-Sea | 3 | 381 | read 06:14 run, 0 retained |
| Ambush on the Minutemen | 3 | 378 | read 06:14 run, 0 retained |
| Attack on the Nefaria Compound/Tech Suits Ambush | 3 | 376 | read 06:14 run, 0 retained |
| Battle on Sovereign | 4 | 376 | read 06:14 run, 0 retained |
| Search for the Magistrate's Son | 3 | 374 | read 06:14 run, 0 retained |
| Theft of Howard Stark's Technology | 3 | 373 | read 06:14 run, 0 retained |
| Arrest of Loki Laufeydottir | 3 | 373 | read 06:14 run, 0 retained |
| Robbery of Sonny's Grocery | 3 | 370 | read 06:14 run, 0 retained |
| Escape from Sokovian Prison | 3 | 361 | read 06:14 run, 0 retained |
| Capture of the Watchdogs | 3 | 359 | read 06:14 run, 0 retained |
| Massacre at the Wedding Party | 3 | 358 | read 06:14 run, 0 retained |
| Infiltration into East Berlin | 3 | 356 | read 06:14 run, 0 retained |
| Raid of the Murdock & McDuffie Law Office | 3 | 355 | read 06:14 run, 0 retained |
| Attack on John McIver | 3 | 350 | read 06:14 run, 0 retained |
| Chase of Sprite | 3 | 350 | read 06:14 run, 0 retained |
| Assassination of Greg Pressfield | 3 | 349 | read 06:14 run, 0 retained |
| Massacre of the Tracksuit Mafia | 4 | 347 | read 06:14 run, 0 retained |
| Ambush on the Gang Leaders | 2 | 333 | read 06:14 run, 0 retained |
| Battle at the Orex II Gravity Well | 3 | 333 | read 06:14 run, 0 retained |
| Arrest of Ariana Iacovou | 3 | 328 | read 06:14 run, 0 retained |
| Attack on Crete | 3 | 322 | read 06:14 run, 0 retained |
| Battle of Troy | 3 | 313 | read 06:14 run, 0 retained |
| Raid of the Lower East Side Housing Project | 3 | 310 | read 06:14 run, 0 retained |
| Ambush on Turk Barrett | 3 | 299 | read 06:14 run, 0 retained |
| Battle of Sudan | 3 | 284 | read 06:14 run, 0 retained |
| Attack on the Yangsi Gonshi Chop Shop | 3 | 283 | read 06:14 run, 0 retained |
| Murder of David Richardson | 3 | 282 | read 06:14 run, 0 retained |
| Assassination of President Ross' Attackers | 3 | 281 | read 06:14 run, 0 retained |
| Virtue Challenge | 2 | 278 | read 06:14 run, 0 retained |
| Liberation of the Maggia-Controlled Villages | 3 | 277 | read 06:14 run, 0 retained |
| Chase of the Maggia Weapons Transport | 3 | 274 | read 06:14 run, 0 retained |
| Assassination of Chantelle Fusilier | 3 | 270 | read 06:14 run, 0 retained |
| Kidnapping of Lia Dewan | 3 | 267 | read 06:14 run, 0 retained |
| Ambush on Jennifer Walters | 3 | 257 | read 06:14 run, 0 retained |
| Attack on Sprite's Host | 3 | 256 | read 06:14 run, 0 retained |
| Liberation of the Multiverse | 3 | 246 | read 06:14 run, 0 retained |
| Capture of Kilgrave | 3 | 244 | read 06:14 run, 0 retained |
| Ambush at the Wakandan Outreach Center | 3 | 241 | read 06:14 run, 0 retained |
| Attack on the Red Dust Cell | 3 | 231 | read 06:14 run, 0 retained |
| Battle of Beijing | 2 | 230 | read 06:14 run, 0 retained |
| Assassination of Dennis Dunphy | 3 | 230 | read 06:14 run, 0 retained |
| Battle at the Sandbox | 3 | 219 | read 06:14 run, 0 retained |
| Theft of the Vibranium Ax/Horde-Infested Earth | 3 | 205 | read 06:14 run, 0 retained |
| Attack on Stark Industries Headquarters | 3 | 203 | read 06:14 run, 0 retained |
| Skirmish for Barnaby | 2 | 193 | read 06:14 run, 0 retained |
| Massacre of the Forest Witches | 3 | 190 | read 06:14 run, 0 retained |
| Battle at the PRIDE Construction Site/Gibborim Escape | 3 | 189 | read 06:14 run, 0 retained |
| Burgos Family Car Crash | 2 | 183 | read 06:14 run, 0 retained |
| Rock and Roll Movie Awards | 3 | 181 | read 06:14 run, 0 retained |
| Escape from Utkin Prison | 3 | 178 | read 06:14 run, 0 retained |
| Attack on Jack Thompson | 2 | 177 | read 06:14 run, 0 retained |
| Battle of Grundar | 2 | 177 | read 06:14 run, 0 retained |
| Theft of the Mark II Iron Man Armor | 3 | 167 | read 06:14 run, 0 retained |
| Invasion of Vanaheim | 3 | 162 | read 06:14 run, 0 retained |
| Attack on A.I.M. Headquarters | 3 | 158 | read 06:14 run, 0 retained |
| Attack on the Somali Pirates' Ship | 3 | 158 | read 06:14 run, 0 retained |
| Battle of Wakanda/Horde-Infested Earth | 3 | 158 | read 06:14 run, 0 retained |
| Capture of the Burglar | 2 | 156 | read 06:14 run, 0 retained |
| Destruction of Ol' Betsy | 3 | 146 | read 06:14 run, 0 retained |
| Chase of the Iron Man Armor | 3 | 138 | read 06:14 run, 0 retained |
| Attack on Deadpool | 3 | 138 | read 06:14 run, 0 retained |
| Chase of the Hydra Spies | 3 | 136 | read 06:14 run, 0 retained |
| Chase of the Intergalactic Ice Cream Truck | 3 | 134 | read 06:14 run, 0 retained |
| Battle of Adwa | 2 | 132 | read 06:14 run, 0 retained |
| Battle at Stark Expo/Gamma-Enhanced Happy Hogan | 2 | 131 | read 06:14 run, 0 retained |
| Robbery of the Maltese Museum | 2 | 131 | read 06:14 run, 0 retained |
| Westview Talent Show | 1 | 128 | read 06:14 run, 0 retained |
| Robbery of the Pym Residence/Ant-Chosen Scott Lang | 3 | 124 | read 06:14 run, 0 retained |
| Battle at the New York Sanctum/Strange Surgeon Christine Palmer | 3 | 119 | read 06:14 run, 0 retained |
| Destruction of Midtown High School | 3 | 104 | read 06:14 run, 0 retained |
| Southern California Law Awards Gala/Uncontrollable She-Hulk | 3 | 93 | read 06:14 run, 0 retained |
| Rescue of Air Force One Passengers/Assisted Air Force One Rescue | 2 | 80 | read 06:14 run, 0 retained |
| Ambush at Alias Investigations Office | 2 | 75 | read 06:14 run, 0 retained |
| Snap/Loyal Daughters of Thanos | 2 | 60 | read 06:14 run, 0 retained |
| Battle for Earth | 2 | 57 | read 06:14 run, 0 retained |
| First Battle of Svartalfheim/Manhattan Avengers Compound | 1 | 57 | read 06:14 run, 0 retained |
| Arrest of Groot | 1 | 47 | read 06:14 run, 0 retained |
| Battle at Stark Expo/Unrestrained Iron Man Duo | 1 | 43 | read 06:14 run, 0 retained |
| Jennifer Walters' Car Crash/Uncontrollable She-Hulk | 2 | 43 | read 06:14 run, 0 retained |
| Duel in the Grand Arena/Hela-Unaware Thor | 1 | 24 | read 06:14 run, 0 retained |
