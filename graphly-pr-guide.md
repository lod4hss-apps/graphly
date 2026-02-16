# Guide PR Graphly (Logre fixes)

Ce document decrit, de maniere detaillee, les modifications a appliquer dans Graphly pour preparer le PR. Il est destine a l agent de codage charge d implementer les corrections.

Objectif general
- Aligner Graphly upstream avec les correctifs necessaires a Logre.
- Supprimer la dependance a une copie locale vendoree dans Logre.
- Garantir un comportement stable pour SHACL, export Turtle et AllegroGraph.

Perimetre
- Fichiers cibles dans Graphly:
  - `graphly/models/shacl.py`
  - `graphly/schema/graph.py`
  - `graphly/sparql/allegrograph.py`
- Aucun changement d API publique, uniquement robustesse et comportement correct.

Pre-requis
- Repo Graphly clone localement.
- Branche dediee (ex: `logre-compat-fixes`).

---

1) SHACL: separation range_class_uri / range_datatype

Contexte
- Dans Logre, certaines shapes utilisent `sh:datatype` pour definir un range literal.
- L implementation actuelle fusionne `datatype` dans `range_class_uri` ce qui perturbe la resolution des classes.

Objectif
- Conserver la valeur `range_class_uri` pour les classes, et gerer `range_datatype` a part.
- Choisir `range_target` comme `range_uri` (classe) ou `range_datatype` (datatype) si present.

Fichier cible
- `graphly/models/shacl.py`

Modifications a faire
1. Dans la requete SPARQL de `get_properties`, ajouter un champ `range_datatype`:

Avant
```python
(COALESCE(?range_class_uri_, ?datatype_, '') as ?range_class_uri)
```

Apres
```python
(COALESCE(?range_class_uri_, '') as ?range_class_uri)
(COALESCE(?datatype_, '') as ?range_datatype)
```

2. Dans la boucle Python, recuperer `range_datatype` et ajuster le calcul du range:

Avant
```python
range_uri = resp.get('range_class_uri')
range = self.find_class(range_uri) if range_uri else None
```

Apres
```python
range_uri = resp.get('range_class_uri')
range_datatype = resp.get('range_datatype')
range_target = range_uri or range_datatype
range = self.find_class(range_target) if range_target else None
```

Remarque
- On ne change pas la signature des classes ni la structure des objets `Property`.

---

2) Graph: dump_turtle plus robuste

Contexte
- Certains endpoints renvoient des objets non str (ou des objets with __str__).
- `dump_turtle` doit proteger contre ces variations sans casser les blank nodes.

Objectif
- Forcer `str()` pour `s`, `p`, `o` avant de passer dans `prepare`.
- Conserver la logique des blank nodes.

Fichier cible
- `graphly/schema/graph.py`

Modifications a faire
Dans `dump_turtle`, remplacer la construction de `s`, `p`, `o` par la version suivante:

```python
subj = str(triple['s'])
obj = triple['o']

if subj.startswith('_:'):
    s = subj
elif triple['s_is_blank'] == 'true':
    s = f"_:{subj}"
else:
    s = prepare(subj, prefixes.shorts())

p = prepare(str(triple['p']), prefixes.shorts())

obj_str = str(obj)
if obj_str.startswith('_:'):
    o = obj_str
elif triple['o_is_blank'] == 'true':
    o = f"_:{obj_str}"
else:
    o = prepare(obj, prefixes.shorts())
```

Remarque
- Ne pas changer `dump_nquad` (la logique reste ok).

---

3) AllegroGraph: prefixes et mutation

Contexte
- AllegroGraph requiert les prefixes `franz` + `franzOption_defaultDatasetBehavior`.
- L implementation actuelle mute `Prefixes` en place, ce qui peut avoir des effets de bord.
- `insert`/`delete` ne transmettent pas `prefixes`.

Objectif
- Toujours ajouter les prefixes requis sans muter l objet partage.
- Ajouter le prefix `franz` (namespace complet) en plus du prefix option.
- Propager `prefixes` dans `insert` et `delete`.

Fichier cible
- `graphly/sparql/allegrograph.py`

Modifications a faire
1. Definir les prefixes requis:

```python
franz_prefix = Prefix('franz', 'http://franz.com/ns/allegrograph/7.0/')
additional_prefix = Prefix('franzOption_defaultDatasetBehavior', 'franz:rdf')
```

2. Mettre a jour `run` pour travailler sur une copie:

```python
required_prefixes = [self.franz_prefix, self.additional_prefix]
if prefixes is None:
    local_prefixes = Prefixes(required_prefixes.copy())
else:
    local_prefixes = Prefixes(prefixes.prefix_list.copy())
    for prefix in required_prefixes:
        if not local_prefixes.has(prefix.short):
            local_prefixes.add(prefix)
return super().run(text, local_prefixes)
```

3. Mettre a jour `insert` pour propager `prefixes`:

```python
def insert(self, triples, graph_uri=None, prefixes=None):
    self.delete(triples, graph_uri, prefixes)
    super().insert(triples, graph_uri, prefixes)
```

Remarques
- Laisser `delete` tel quel si sa signature accepte `prefixes` dans la classe parente.
- Conserver `technology_name = 'Allegrograph'`.

---

Verification minimale
- Lint basique (si present) ou au moins import des modules modifies.
- Pas de tests automatise requis, mais verifier que les imports restent valides.

Message de commit propose
- `Fix SHACL range datatype handling and AllegroGraph prefixes`

PR description (synthese)
- Stabilise SHACL range handling by separating datatype and class range.
- Harden Graph.dump_turtle string casting for blank nodes.
- Ensure AllegroGraph required prefixes without mutating shared Prefixes.

---

Notes
- Aucun changement dans Logre ici; ce PR vise uniquement Graphly.
- Ces correctifs doivent ensuite etre pinnees dans Logre (requirements) jusqu au merge upstream.
