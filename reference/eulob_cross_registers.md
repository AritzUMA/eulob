# Find Organization Names Shared Across Lobbying Registers

Identify names occurring in multiple territorial lobbying registers in
the bundled EU-LOB catalogue.

## Usage

``` r
eulob_cross_registers(name = NULL, min_countries = 2L, limit = NULL)
```

## Arguments

- name:

  Optional organization name for exact normalized matching. Matching is
  case-insensitive, but not fuzzy.

- min_countries:

  Positive integer specifying the minimum number of territorial scopes.
  Default is 2.

- limit:

  Optional positive integer limiting distinct names.

## Value

A data frame containing name_id, name, country, register, lobby_id,
n_countries and n_entities.

## Details

Matching uses normalized organization names and existing name
identifiers. A shared name is not proof that registrations refer to the
same legal entity.

The EU Transparency Register ("UE") counts as a separate scope. The
limit is applied to names, not registration rows.

## See also

\[eulob_lobbies()\], \[eulob_search()\]

## Examples

``` r
eulob_cross_registers(limit = 5)
#>                                                             name_id
#> 1  e2647646f9d6444f4c759e263cabef421fbb961939c41dc2c8a1aa1056974663
#> 2  e2647646f9d6444f4c759e263cabef421fbb961939c41dc2c8a1aa1056974663
#> 3  e2647646f9d6444f4c759e263cabef421fbb961939c41dc2c8a1aa1056974663
#> 4  e2647646f9d6444f4c759e263cabef421fbb961939c41dc2c8a1aa1056974663
#> 5  1a187dafc1ca54f2a357cbc02fb65c7eaec6e7eb1b23237d4751f7c2e935fb36
#> 6  1a187dafc1ca54f2a357cbc02fb65c7eaec6e7eb1b23237d4751f7c2e935fb36
#> 7  1a187dafc1ca54f2a357cbc02fb65c7eaec6e7eb1b23237d4751f7c2e935fb36
#> 8  1a187dafc1ca54f2a357cbc02fb65c7eaec6e7eb1b23237d4751f7c2e935fb36
#> 9  69d9f7657d4a7ec043cfec0a850137dad26fab1b5bb4bbf3e9182ad667fc0c9d
#> 10 69d9f7657d4a7ec043cfec0a850137dad26fab1b5bb4bbf3e9182ad667fc0c9d
#> 11 69d9f7657d4a7ec043cfec0a850137dad26fab1b5bb4bbf3e9182ad667fc0c9d
#> 12 69d9f7657d4a7ec043cfec0a850137dad26fab1b5bb4bbf3e9182ad667fc0c9d
#> 13 74c860f63661b29cd747cf485fb26898163066cb84328f3855f877dbbeef5d56
#> 14 74c860f63661b29cd747cf485fb26898163066cb84328f3855f877dbbeef5d56
#> 15 74c860f63661b29cd747cf485fb26898163066cb84328f3855f877dbbeef5d56
#> 16 74c860f63661b29cd747cf485fb26898163066cb84328f3855f877dbbeef5d56
#> 17 51f6056b315f252ce7d91b0e84c69715729f3b346002c0ddaa1410f2eae286a2
#> 18 51f6056b315f252ce7d91b0e84c69715729f3b346002c0ddaa1410f2eae286a2
#> 19 51f6056b315f252ce7d91b0e84c69715729f3b346002c0ddaa1410f2eae286a2
#> 20 51f6056b315f252ce7d91b0e84c69715729f3b346002c0ddaa1410f2eae286a2
#>                                    name country
#> 1                               Blic Oy      FI
#> 2                               Blic Oy      GR
#> 3                               BLIC OY      PL
#> 4                               Blic Oy      UE
#> 5  Ontario Teachers' Pension Plan Board      DE
#> 6  Ontario Teachers' Pension Plan Board      FI
#> 7  ONTARIO TEACHERS' PENSION PLAN BOARD      FR
#> 8  Ontario Teachers' Pension Plan Board      UE
#> 9                                Pfizer      BE
#> 10                               Pfizer      EE
#> 11                               PFIZER      FR
#> 12                               Pfizer      IE
#> 13                                 Uber      BE
#> 14                                 Uber      EE
#> 15                                 Uber      IE
#> 16                                 Uber      UE
#> 17                       APCO WORLDWIDE      FR
#> 18                       APCO Worldwide      IT
#> 19                       APCO Worldwide      IT
#> 20                       APCO Worldwide      UE
#>                                 register
#> 1          Finnish Transparency Register
#> 2                Greek Lobbying Register
#> 3  Polish Professional Lobbying Register
#> 4               EU Transparency Register
#> 5                  German Lobby Register
#> 6          Finnish Transparency Register
#> 7                  French HATVP Register
#> 8               EU Transparency Register
#> 9         Belgian Chamber Lobby Register
#> 10               Estonian Lobby Meetings
#> 11                 French HATVP Register
#> 12            Irish Register of Lobbying
#> 13        Belgian Chamber Lobby Register
#> 14               Estonian Lobby Meetings
#> 15            Irish Register of Lobbying
#> 16              EU Transparency Register
#> 17                 French HATVP Register
#> 18                Italian MIMIT Register
#> 19                   Camera dei Deputati
#> 20              EU Transparency Register
#>                                                                 lobby_id
#> 1                                                                   2257
#> 2                                                                     56
#> 3                                                                  00651
#> 4                                                        687078815005-93
#> 5                                                                R000355
#> 6                                                                   1496
#> 7                                                             H148213940
#> 8                                                        819909040311-18
#> 9                                                                 Pfizer
#> 10 name:69d9f7657d4a7ec043cfec0a850137dad26fab1b5bb4bbf3e9182ad667fc0c9d
#> 11                                                             433623550
#> 12                                                                   160
#> 13                                                                  Uber
#> 14 name:74c860f63661b29cd747cf485fb26898163066cb84328f3855f877dbbeef5d56
#> 15                                                                  1153
#> 16                                                       002278013515-26
#> 17                                                             408747368
#> 18                                                 2026-1779209489618-15
#> 19                                                                   353
#> 20                                                        81995781088-41
#>    n_countries n_entities
#> 1            4          4
#> 2            4          4
#> 3            4          4
#> 4            4          4
#> 5            4          4
#> 6            4          4
#> 7            4          4
#> 8            4          4
#> 9            4          4
#> 10           4          4
#> 11           4          4
#> 12           4          4
#> 13           4          4
#> 14           4          4
#> 15           4          4
#> 16           4          4
#> 17           3          4
#> 18           3          4
#> 19           3          4
#> 20           3          4
eulob_cross_registers("Grünenthal GmbH")
#>                                                            name_id
#> 1 73ec106774dba842396b156111fac93cc42f7d341bf786ae523b269af2136075
#> 2 73ec106774dba842396b156111fac93cc42f7d341bf786ae523b269af2136075
#> 3 73ec106774dba842396b156111fac93cc42f7d341bf786ae523b269af2136075
#>              name country                   register       lobby_id n_countries
#> 1 Grünenthal GmbH      DE      German Lobby Register        R005914           3
#> 2 Grünenthal GmbH      IE Irish Register of Lobbying           1446           3
#> 3 Grünenthal GmbH      UE   EU Transparency Register 67826544528-01           3
#>   n_entities
#> 1          3
#> 2          3
#> 3          3
eulob_cross_registers(min_countries = 3, limit = 10)
#>                                                             name_id
#> 1  e2647646f9d6444f4c759e263cabef421fbb961939c41dc2c8a1aa1056974663
#> 2  e2647646f9d6444f4c759e263cabef421fbb961939c41dc2c8a1aa1056974663
#> 3  e2647646f9d6444f4c759e263cabef421fbb961939c41dc2c8a1aa1056974663
#> 4  e2647646f9d6444f4c759e263cabef421fbb961939c41dc2c8a1aa1056974663
#> 5  1a187dafc1ca54f2a357cbc02fb65c7eaec6e7eb1b23237d4751f7c2e935fb36
#> 6  1a187dafc1ca54f2a357cbc02fb65c7eaec6e7eb1b23237d4751f7c2e935fb36
#> 7  1a187dafc1ca54f2a357cbc02fb65c7eaec6e7eb1b23237d4751f7c2e935fb36
#> 8  1a187dafc1ca54f2a357cbc02fb65c7eaec6e7eb1b23237d4751f7c2e935fb36
#> 9  69d9f7657d4a7ec043cfec0a850137dad26fab1b5bb4bbf3e9182ad667fc0c9d
#> 10 69d9f7657d4a7ec043cfec0a850137dad26fab1b5bb4bbf3e9182ad667fc0c9d
#> 11 69d9f7657d4a7ec043cfec0a850137dad26fab1b5bb4bbf3e9182ad667fc0c9d
#> 12 69d9f7657d4a7ec043cfec0a850137dad26fab1b5bb4bbf3e9182ad667fc0c9d
#> 13 74c860f63661b29cd747cf485fb26898163066cb84328f3855f877dbbeef5d56
#> 14 74c860f63661b29cd747cf485fb26898163066cb84328f3855f877dbbeef5d56
#> 15 74c860f63661b29cd747cf485fb26898163066cb84328f3855f877dbbeef5d56
#> 16 74c860f63661b29cd747cf485fb26898163066cb84328f3855f877dbbeef5d56
#> 17 51f6056b315f252ce7d91b0e84c69715729f3b346002c0ddaa1410f2eae286a2
#> 18 51f6056b315f252ce7d91b0e84c69715729f3b346002c0ddaa1410f2eae286a2
#> 19 51f6056b315f252ce7d91b0e84c69715729f3b346002c0ddaa1410f2eae286a2
#> 20 51f6056b315f252ce7d91b0e84c69715729f3b346002c0ddaa1410f2eae286a2
#> 21 575ec7ac6ca47bbfa2882d49fd02d64e871549d9c465423c7108afc90b5fc85b
#> 22 575ec7ac6ca47bbfa2882d49fd02d64e871549d9c465423c7108afc90b5fc85b
#> 23 575ec7ac6ca47bbfa2882d49fd02d64e871549d9c465423c7108afc90b5fc85b
#> 24 575ec7ac6ca47bbfa2882d49fd02d64e871549d9c465423c7108afc90b5fc85b
#> 25 3ab2fef92c7c1d8d699731dcf50db2db02a33cf54f5b24d5b937390df5760430
#> 26 3ab2fef92c7c1d8d699731dcf50db2db02a33cf54f5b24d5b937390df5760430
#> 27 3ab2fef92c7c1d8d699731dcf50db2db02a33cf54f5b24d5b937390df5760430
#> 28 56046651cb41a568d41c68b7a66cea7d7e6322a08675f2e2a01263f3fd0db69e
#> 29 56046651cb41a568d41c68b7a66cea7d7e6322a08675f2e2a01263f3fd0db69e
#> 30 56046651cb41a568d41c68b7a66cea7d7e6322a08675f2e2a01263f3fd0db69e
#> 31 0183d59c1f799dfd793d2e5d48adee6f92f25e79a001dd804caa449dc9674bbd
#> 32 0183d59c1f799dfd793d2e5d48adee6f92f25e79a001dd804caa449dc9674bbd
#> 33 0183d59c1f799dfd793d2e5d48adee6f92f25e79a001dd804caa449dc9674bbd
#> 34 cbc178d323c38870cb06b08a519556d994ee4d6ce9dedd49040798782e5e0fa4
#> 35 cbc178d323c38870cb06b08a519556d994ee4d6ce9dedd49040798782e5e0fa4
#> 36 cbc178d323c38870cb06b08a519556d994ee4d6ce9dedd49040798782e5e0fa4
#>                                    name country
#> 1                               Blic Oy      FI
#> 2                               Blic Oy      GR
#> 3                               BLIC OY      PL
#> 4                               Blic Oy      UE
#> 5  Ontario Teachers' Pension Plan Board      DE
#> 6  Ontario Teachers' Pension Plan Board      FI
#> 7  ONTARIO TEACHERS' PENSION PLAN BOARD      FR
#> 8  Ontario Teachers' Pension Plan Board      UE
#> 9                                Pfizer      BE
#> 10                               Pfizer      EE
#> 11                               PFIZER      FR
#> 12                               Pfizer      IE
#> 13                                 Uber      BE
#> 14                                 Uber      EE
#> 15                                 Uber      IE
#> 16                                 Uber      UE
#> 17                       APCO WORLDWIDE      FR
#> 18                       APCO Worldwide      IT
#> 19                       APCO Worldwide      IT
#> 20                       APCO Worldwide      UE
#> 21                   Gasgrid Finland OY      EE
#> 22                   Gasgrid Finland Oy      FI
#> 23                   Gasgrid Finland Oy      FI
#> 24                   Gasgrid Finland Oy      UE
#> 25                               AbbVie      BE
#> 26                               ABBVIE      FR
#> 27                               AbbVie      UE
#> 28                          BNP PARIBAS      FR
#> 29                          BNP PARIBAS      IE
#> 30                          BNP PARIBAS      UE
#> 31            Compagnie de Saint-Gobain      DE
#> 32            COMPAGNIE DE SAINT-GOBAIN      FR
#> 33            Compagnie de SAINT-GOBAIN      UE
#> 34          DAIKIN CHEMICAL EUROPE GmbH      DE
#> 35          DAIKIN CHEMICAL EUROPE GMBH      FR
#> 36          Daikin Chemical Europe GmbH      UE
#>                                 register
#> 1          Finnish Transparency Register
#> 2                Greek Lobbying Register
#> 3  Polish Professional Lobbying Register
#> 4               EU Transparency Register
#> 5                  German Lobby Register
#> 6          Finnish Transparency Register
#> 7                  French HATVP Register
#> 8               EU Transparency Register
#> 9         Belgian Chamber Lobby Register
#> 10               Estonian Lobby Meetings
#> 11                 French HATVP Register
#> 12            Irish Register of Lobbying
#> 13        Belgian Chamber Lobby Register
#> 14               Estonian Lobby Meetings
#> 15            Irish Register of Lobbying
#> 16              EU Transparency Register
#> 17                 French HATVP Register
#> 18                Italian MIMIT Register
#> 19                   Camera dei Deputati
#> 20              EU Transparency Register
#> 21               Estonian Lobby Meetings
#> 22         Finnish Transparency Register
#> 23         Finnish Transparency Register
#> 24              EU Transparency Register
#> 25        Belgian Chamber Lobby Register
#> 26                 French HATVP Register
#> 27              EU Transparency Register
#> 28                 French HATVP Register
#> 29            Irish Register of Lobbying
#> 30              EU Transparency Register
#> 31                 German Lobby Register
#> 32                 French HATVP Register
#> 33              EU Transparency Register
#> 34                 German Lobby Register
#> 35                 French HATVP Register
#> 36              EU Transparency Register
#>                                                                 lobby_id
#> 1                                                                   2257
#> 2                                                                     56
#> 3                                                                  00651
#> 4                                                        687078815005-93
#> 5                                                                R000355
#> 6                                                                   1496
#> 7                                                             H148213940
#> 8                                                        819909040311-18
#> 9                                                                 Pfizer
#> 10 name:69d9f7657d4a7ec043cfec0a850137dad26fab1b5bb4bbf3e9182ad667fc0c9d
#> 11                                                             433623550
#> 12                                                                   160
#> 13                                                                  Uber
#> 14 name:74c860f63661b29cd747cf485fb26898163066cb84328f3855f877dbbeef5d56
#> 15                                                                  1153
#> 16                                                       002278013515-26
#> 17                                                             408747368
#> 18                                                 2026-1779209489618-15
#> 19                                                                   353
#> 20                                                        81995781088-41
#> 21 name:575ec7ac6ca47bbfa2882d49fd02d64e871549d9c465423c7108afc90b5fc85b
#> 22                                                                   109
#> 23                                                                  2630
#> 24                                                       159590251110-94
#> 25                                                                AbbVie
#> 26                                                             750775660
#> 27                                                       934069612666-51
#> 28                                                             662042449
#> 29                                                                  3720
#> 30                                                        78787381113-69
#> 31                                                               R005253
#> 32                                                             542039532
#> 33                                                       892857311821-20
#> 34                                                               R005819
#> 35                                                             981629975
#> 36                                                       292206436409-62
#>    n_countries n_entities
#> 1            4          4
#> 2            4          4
#> 3            4          4
#> 4            4          4
#> 5            4          4
#> 6            4          4
#> 7            4          4
#> 8            4          4
#> 9            4          4
#> 10           4          4
#> 11           4          4
#> 12           4          4
#> 13           4          4
#> 14           4          4
#> 15           4          4
#> 16           4          4
#> 17           3          4
#> 18           3          4
#> 19           3          4
#> 20           3          4
#> 21           3          4
#> 22           3          4
#> 23           3          4
#> 24           3          4
#> 25           3          3
#> 26           3          3
#> 27           3          3
#> 28           3          3
#> 29           3          3
#> 30           3          3
#> 31           3          3
#> 32           3          3
#> 33           3          3
#> 34           3          3
#> 35           3          3
#> 36           3          3
```
