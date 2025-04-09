# Rapport d'analyse : Jeux sortis en 2024 (Grouvee)

Ce rapport présente une analyse des jeux vidéo sortis en 2024, basée sur les données collectées sur le site Grouvee. Il a pour but de mieux comprendre les tendances de l'industrie vidéoludique de cette année-là à travers différents indicateurs : notes moyennes, genres populaires, répartition par plateforme, etc.

## Objectifs de l'étude

- Identifier les genres et types de jeux les plus populaires en 2024.
- Étudier la distribution des notes moyennes données par les utilisateurs.
- Comparer les performances des jeux selon les plateformes.
- Explorer l'impact d'une franchise sur les évaluations.
- Appliquer des techniques de clustering pour détecter des groupes de jeux similaires.
- Vérifier les corrélations entre certaines variables clés.

---

## 1. Tendance générale des notes

Distribution des notes moyennes des jeux :

![Distribution](../images/distribution_notes.png)

Courbe de densité des notes :

![Densité](../images/courbe_de_densite.png)

Boxplot général des notes moyennes :

![Boxplot](../images/rep_glob_des_notes_moy.png)

**Analyse :**
> La majorité des jeux obtiennent des notes comprises entre 3 et 4.5. On note une légère asymétrie vers les hautes valeurs, traduisant une tendance globale positive des utilisateurs.

---

## 2. Comparaison des genres

Boxplot des notes par genre :

![Boxplot genres](../images/boxplot.png)

Répartition des jeux par genre :

![Colonnes genres](../images/jeux_par_genre_treemp.png)

**Analyse :**
> Certains genres comme les RPG ou les jeux d'aventure obtiennent généralement de meilleures notes. Les genres plus niches montrent une plus grande variabilité.

---

## 3. Plateformes et notes

Distribution des notes individuelles par plateforme :

![Boxplot plateformes](../images/note_indiv_par_platf.png)

Note moyenne par plateforme :

![Colonnes plateformes](../images/note_moyenne_jeux_par_plateforme.png)

**Analyse :**
> Les jeux PC et PlayStation tendent à avoir de bonnes évaluations. La variabilité peut indiquer une diversité plus importante dans la qualité des jeux selon la plateforme.

---

## 4. Clustering des jeux

Clustering basé sur la note moyenne et le nombre de plateformes :

![Clustering](../images/clustering.png)

**Analyse :**
> Trois groupes se dessinent : (1) des jeux peu notés, (2) jeux multi-plateformes avec notes moyennes, et (3) jeux très bien notés, parfois exclusifs.

---

## 5. Corrélation

Matrice de corrélation entre note moyenne et nombre de plateformes :

![Corrélation](../images/correlation.png)

**Analyse :**
> La corrélation est faible mais positive (~0.12) : les jeux disponibles sur plus de plateformes ont tendance à obtenir légèrement de meilleures notes.

---

## 6. Fréquence développeurs

Nombre de jeux par développeur :

![Développeurs](../images//dev_freq.png)

**Analyse :**
> Quelques développeurs se démarquent par leur productivité. On pourra aller plus loin en croisant avec la qualité moyenne de leurs jeux.

---

## 7. Évolution temporelle

Évolution mensuelle du nombre de jeux et de la note moyenne :

![Évolution](../images/jeux_par_mois.png)

**Analyse :**
> Les mois de janvier, octobre et decembre montrent des pics de sorties. Les notes restent globalement stables avec de légères hausses selon les mois.

---

## 8. Franchises

Comparaison des notes entre jeux avec ou sans franchise :

![Franchise](../images/noteavecousansfranchise.png)

**Analyse :**
> Les jeux appartenant à une franchise ont tendance à obtenir de meilleures évaluations. Cela suggère que l'appartenance à un univers connu rassure ou fidélise les joueurs.

---

## Conclusion

Cette étude exploratoire met en lumière plusieurs dynamiques du marché vidéoludique 2024. Elle montre que certaines plateformes ou genres sont mieux notés que d'autres, que les franchises influencent la perception des utilisateurs, et que des patterns intéressants émergent grâce aux techniques de clustering.

> Des études futures pourraient inclure des données historiques, intégrer le temps de jeu ou encore les commentaires textuels pour enrichir cette analyse.

---

**Fait avec :** R, ggplot2, dplyr, fviz_cluster, treemapify
