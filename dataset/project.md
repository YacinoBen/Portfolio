# 📸 Capture Moment

**Capture Moment** est une application open source (GPLv3) et multiplateforme (desktop et mobile) d'édition photo non destructive. Conçue pour les photographes professionnels et amateurs éclairés, elle offre un workflow moderne, performant et fidèle aux couleurs, combinant le dématricage RAW, le catalogage et une gestion de la couleur de niveau professionnel.

---

## 🎯 Objectif du Projet

Capture Moment a pour ambition de devenir une alternative open source performante et modulaire aux logiciels de retouche majeurs du marché. L'application met l'accent sur :
* Un **workflow non destructif** respectant l'intégrité des fichiers originaux.
* La **précision colorimétrique** indispensable aux exigences des professionnels.
* Des **performances élevées** grâce à une architecture logicielle optimisée et le traitement d'image accéléré.

---

## ✨ Fonctionnalités Clés

* **Traitement RAW Avancé** : Prise en charge des principaux formats RAW du marché via OpenImageIO.
* **Pipeline Non Destructif** : Sauvegarde des ajustements et modifications dans des fichiers sidecar XMP.
* **Catalogage Intelligent** : Indexation rapide, collections, mots-clés et recherche avancée gérés par SQLite.
* **Gestion Professionnelle de la Couleur** : Intégration prévue d'OpenColorIO pour une fidélité optimale des espaces colorimétriques.
* **Profils Appareils (DCP)** : Correction chromatique automatique selon le modèle du capteur (intégration prévue).
* **Interface Moderne (GUI)** : Interface fluide, réactive et accélérée matériellement grâce à Qt6 Quick / QML.
* **Multiplateforme** : Compatible Windows, macOS, Linux, et conçu pour être déployable sur mobile (iOS / Android).
* **Haute Performance** : Pipeline de calculs ultra-rapides optimisé par Halide et système de cache intelligent via OIIO.
* **Benchmarking Intégré** : Outils de mesure de performance intégrés pour garantir la réactivité de l'application.

---

## 🛠️ Stack Technique & Architecture

Capture Moment repose sur un écosystème C++20/C++23 moderne et modulaire, sélectionnant les meilleures bibliothèques open source pour chaque problématique technique :

| Composant | Technologie | Rôle & Usage |
| :--- | :--- | :--- |
| **Langage Core** | **C++20 / C++23** | Logique métier, performances brutes et gestion mémoire. |
| **Build System** | **CMake 4.2+** | Configuration du build multiplateforme. |
| **I/O & Cache** | **OpenImageIO** | Lecture/Écriture de tous les formats d'images et cache par tuiles (*tile-based*). |
| **Traitement d'Image** | **Halide** | Optimisation du pipeline de traitement d'image haute performance. |
| **Interface Graphique** | **Qt6 Quick / QML** | UI déclarative, moderne et accélérée matériellement. |
| **Gestion des Couleurs**| **OpenColorIO** | Prise en charge des espaces colorimétriques standards de l'industrie. |
| **Catalogage & Index** | **SQLite** | Base de données embarquée rapide pour le moteur de recherche et l'indexation. |
| **Métadonnées & Settings**| **Exiv2 (XMP) / JSON** | Stockage des ajustements en XMP et des paramètres de l'application en JSON. |

---

## 🔗 Liens & Ressources

* **Dépôt GitHub** : [YacinoBen/CaptureMoment](https://github.com/YacinoBen/CaptureMoment)
* **Architecture** : Consulter la *General Architecture Document* sur le dépôt pour le détail des choix techniques et de la roadmap.
* **Installation & Build** : Guide de compilation disponible pour Windows, macOS, Linux et les gestionnaires de paquets (Vcpkg, Homebrew, apt/dnf).

