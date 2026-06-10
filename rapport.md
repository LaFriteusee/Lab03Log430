# Rapport - Labo 03 : REST APIs, GraphQL

**Étudiant :** Thomas Journault  
**Cours :** LOG430 - Architecture logicielle  

---

## Question 1

Dans la [RFC 7231](https://www.rfc-editor.org/rfc/rfc7231#section-4.2.1), nous trouvons que certaines méthodes HTTP sont considérées comme sûres (__safe__) ou idempotentes, en fonction de leur capacité à modifier (ou non) l'état de l'application. Parmi les méthodes utilisées dans l'activité 2 (`POST /products`, `POST /stocks`, `GET /stocks/:id`, `POST /orders`, `DELETE /orders/:id`), lesquelles sont sûres, non sûres, idempotentes et/ou non idempotentes ?

---

## Question 2

Décrivez l'utilisation de la méthode `join` dans le cas de `get_stock_for_all_products`. Utilisez les méthodes telles que décrites à *Simple Relationship Joins* et *Joins to a Target with an ON Clause* dans la documentation SQLAlchemy pour ajouter les colonnes `name`, `sku` et `price`. Veuillez inclure le code pour illustrer votre réponse.

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
