# Rapport - Labo 03 : REST APIs, GraphQL

**Étudiant :** Thomas Journault  
**Cours :** LOG430 - Architecture logicielle  

---

## Question 1

Dans la [RFC 7231](https://www.rfc-editor.org/rfc/rfc7231#section-4.2.1), nous trouvons que certaines méthodes HTTP sont considérées comme sûres (__safe__) ou idempotentes, en fonction de leur capacité à modifier (ou non) l'état de l'application. Parmi les méthodes utilisées dans l'activité 2 (`POST /products`, `POST /stocks`, `GET /stocks/:id`, `POST /orders`, `DELETE /orders/:id`), lesquelles sont sûres, non sûres, idempotentes et/ou non idempotentes ?

Selon les sections 4.2.1 et 4.2.2 de la RFC 7231, une méthode est **sûre** si elle ne modifie pas l'état du serveur, et **idempotente** si plusieurs appels identiques produisent le même résultat qu'un seul appel.

Voici l'analyse des méthodes utilisées dans l'activité 2 :

| Méthode | Endpoint | Sûre | Idempotente |
|---|---|---|---|
| `GET` | `GET /stocks/:id` |  Oui |  Oui |
| `POST` | `POST /products`, `POST /stocks`, `POST /orders` |  Non |  Non |
| `DELETE` | `DELETE /orders/:id` |  Non |  Oui |

**`GET /stocks/:id`** — sûre et idempotente. Elle ne fait que lire le stock d'un produit sans modifier l'état de l'application. Appeler cet endpoint plusieurs fois retourne toujours la même réponse.

```python
# store_manager.py
@app.get('/stocks/<int:product_id>')
def get_stocks(product_id):
    return get_stock(product_id)
```

**`POST /products`, `POST /stocks`, `POST /orders`** — ni sûres, ni idempotentes. Chaque appel crée une nouvelle ressource ou modifie l'état. Par exemple, deux appels identiques à `POST /orders` créent deux commandes distinctes et déduisent le stock deux fois.

```python
# store_manager.py
@app.post('/orders')
def post_orders():
    return create_order(request)  # crée une nouvelle commande à chaque appel

@app.post('/products')
def post_products():
    return create_product(request)  # crée un nouveau produit à chaque appel
```

**`DELETE /orders/:id`** — non sûre (elle modifie l'état en supprimant la commande et en remettant le stock), mais idempotente : supprimer une commande déjà supprimée retourne simplement `{"deleted": false}` sans effet secondaire.

```python
# store_manager.py
@app.delete('/orders/<int:order_id>')
def delete_orders_id(order_id):
    return remove_order(order_id)  # idempotent : supprimer deux fois = même résultat
```

---

## Question 2

Décrivez l'utilisation de la méthode `join` dans le cas de `get_stock_for_all_products`. Utilisez les méthodes telles que décrites à *Simple Relationship Joins* et *Joins to a Target with an ON Clause* dans la documentation SQLAlchemy pour ajouter les colonnes `name`, `sku` et `price`. Veuillez inclure le code pour illustrer votre réponse.

La méthode `join` de SQLAlchemy permet de combiner deux tables en une seule requête, évitant ainsi de faire plusieurs appels séparés à la base de données.

**Pourquoi ne pas utiliser Simple Relationship Joins**

La documentation SQLAlchemy décrit le *Simple Relationship Join* comme suit :

```python
# Exemple de la doc — fonctionne quand une relationship() est déclarée
session.query(User).join(User.addresses)
```

Cette syntaxe fonctionne uniquement lorsqu'une `relationship()` est déclarée dans le modèle SQLAlchemy. Dans notre cas, `Stock` et `Product` sont deux modèles indépendants sans `relationship()` définie entre eux :

```python
# src/stocks/models/stock.py
class Stock(Base):
    __tablename__ = 'stocks'
    product_id = Column(Integer, primary_key=True, nullable=False)
    quantity = Column(Integer, nullable=False)
    # Pas de relationship() vers Product

# src/stocks/models/product.py
class Product(Base):
    __tablename__ = 'products'
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String, nullable=False)
    sku = Column(String, nullable=False)
    price = Column(Float, nullable=False)
```

**Utilisation de Joins to a Target with an ON Clause**

Sans `relationship()`, on utilise le style *Joins to a Target with an ON Clause* en passant explicitement la condition de jointure. Cela correspond à l'équivalent SQL `JOIN ... ON` :

```python
# src/stocks/queries/read_stock.py
def get_stock_for_all_products():
    session = get_sqlalchemy_session()
    results = session.query(
        Stock.product_id,
        Stock.quantity,
        Product.name,
        Product.sku,
        Product.price,
    ).join(Product, Stock.product_id == Product.id).all()
```

Le `.join(Product, Stock.product_id == Product.id)` indique à SQLAlchemy de faire une jointure entre la table `stocks` et la table `products` sur la condition `stocks.product_id = products.id`. Cela génère la requête SQL suivante :

```sql
SELECT stocks.product_id, stocks.quantity, products.name, products.sku, products.price
FROM stocks JOIN products ON stocks.product_id = products.id
```

Chaque ligne du résultat contient ainsi les colonnes des deux tables, ce qui permet de construire le rapport complet :

```python
    for row in results:
        stock_data.append({
            'Article': row.name,
            'Numéro SKU': row.sku,
            'Prix unitaire': row.price,
            'Unités en stock': int(row.quantity),
        })
```

---

## Question 3

Quels résultats avez-vous obtenus en utilisant l'endpoint `POST /stocks/graphql-query` avec la requête suggérée ? Veuillez joindre la sortie de votre requête dans Postman afin d'illustrer votre réponse.

```graphql
{
  product(id: "1") {
    id
    quantity
  }
}
```

---

## Question 4

Quelles lignes avez-vous changé dans `update_stock_redis` (fichier `src/stocks/commands/write_stock.py`) ? Veuillez joindre du code afin d'illustrer votre réponse.

---

## Question 5

Quels résultats avez-vous obtenus en utilisant l'endpoint `POST /stocks/graphql-query` avec les améliorations de l'activité 5 ? Veuillez joindre la sortie de votre requête dans Postman afin d'illustrer votre réponse.

---

## Question 6

Examinez attentivement le fichier `docker-compose.yml` du répertoire `scripts`, ainsi que celui situé à la racine du projet. Qu'ont-ils en commun ? Par quel mécanisme ces conteneurs peuvent-ils communiquer entre eux ? Veuillez joindre du code YML afin d'illustrer votre réponse.
