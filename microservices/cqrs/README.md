# CQRS with Event Broker - Documentation

## 🏗️ Architecture CQRS avec Event Broker

Cette implémentation du pattern **CQRS (Command Query Responsibility Segregation)** avec **Event Broker** sépare les opérations d'écriture (Commands) et de lecture (Queries) pour optimiser les performances et la scalabilité.

### 🎯 Objectifs du CQRS

1. **Séparation des Responsabilités**: Commands pour l'écriture, Queries pour la lecture
2. **Modèles Optimisés**: Read Models dénormalisés pour des requêtes rapides  
3. **Scalabilité Indépendante**: Scaling séparé des sides Command et Query
4. **Consistance Éventuelle**: Synchronisation via events et projections
5. **Analytics Avancées**: Aggregations et statistiques en temps réel

### 📋 Architecture Components

```
┌─────────────────┐    Events    ┌──────────────────┐    Projections    ┌─────────────────┐
│   Command Side  │─────────────▶│   Event Broker   │──────────────────▶│   Query Side    │
│                 │              │   (RabbitMQ)     │                   │                 │
│ - Commands      │              │                  │                   │ - Read Models   │
│ - Command       │              │ - Event Routing  │                   │ - Query         │
│   Handlers      │              │ - Event Storage  │                   │   Handlers      │
│ - Write Models  │              │ - Message Queue  │                   │ - Projectors    │
└─────────────────┘              └──────────────────┘                   └─────────────────┘
         │                                                                        │
         ▼                                                                        ▼
┌─────────────────┐                                                    ┌─────────────────┐
│  Domain Events  │                                                    │  MongoDB Read   │
│                 │                                                    │     Store       │
│ - OrderCreated  │                                                    │                 │
│ - PaymentProc.  │                                                    │ - Orders View   │
│ - InventoryUpd. │                                                    │ - Inventory     │
└─────────────────┘                                                    │ - User Summary  │
                                                                       │ - Statistics    │
                                                                       └─────────────────┘
```

### 🔧 Services CQRS

#### 1. **Command Service** (Port 8010)
- **Responsabilité**: Traiter les commandes d'écriture
- **Endpoints**:
  - `POST /commands/orders` - Créer une commande
  - `POST /commands/payments` - Traiter un paiement  
  - `POST /commands/inventory` - Mettre à jour l'inventaire
- **Pattern**: Command Handler → Event Publisher → RabbitMQ

#### 2. **Query Service** (Port 8011) 
- **Responsabilité**: Traiter les requêtes de lecture
- **Endpoints**:
  - `GET /queries/orders/{id}` - Détails d'une commande
  - `GET /queries/users/{id}/orders` - Commandes d'un utilisateur
  - `GET /queries/inventory` - État de l'inventaire
  - `GET /queries/statistics/orders` - Statistiques des commandes
- **Pattern**: Query Handler → MongoDB Read Store

#### 3. **Projection Service** (Background)
- **Responsabilité**: Mettre à jour les Read Models depuis les events
- **Fonctionnement**: Event Subscriber → Event Projector → Read Store Update
- **Projectors**:
  - `OrderProjector` - Met à jour les vues des commandes
  - `InventoryProjector` - Met à jour les vues d'inventaire  
  - `UserSummaryProjector` - Met à jour les résumés utilisateurs

### 📊 Read Models Optimisés

#### OrderReadModel
```json
{
  "order_id": "uuid",
  "user_id": 123,
  "user_email": "user@example.com",
  "total_amount": 99.99,
  "status": "PAID",
  "items": [...],
  "payment_info": {...},
  "timeline": [
    {"event": "OrderInitiated", "timestamp": "..."},
    {"event": "OrderValidated", "timestamp": "..."},
    {"event": "OrderPaid", "timestamp": "..."}
  ]
}
```

#### InventoryReadModel
```json
{
  "product_id": 456,
  "product_name": "Product Name",
  "available_quantity": 98,
  "reserved_quantity": 2,
  "total_quantity": 100,
  "low_stock_alert": false,
  "pending_orders": [...]
}
```

#### UserOrderSummaryReadModel
```json
{
  "user_id": 123,
  "total_orders": 5,
  "total_spent": 499.95,
  "avg_order_value": 99.99,
  "favorite_products": [...],
  "order_statuses": {"COMPLETED": 3, "SHIPPED": 2}
}
```

### 🔄 Event Flow

1. **Command Reception**: Client envoie une commande au Command Service
2. **Command Processing**: Command Handler traite la commande
3. **Event Publication**: Event publié vers RabbitMQ Event Broker
4. **Event Distribution**: RabbitMQ route l'event vers les subscribers
5. **Event Projection**: Projection Service met à jour les Read Models
6. **Query Processing**: Client peut interroger les Read Models optimisés

### 🚀 Comment Utiliser

#### 1. Démarrer les Services
```bash
docker-compose up cqrs_command cqrs_query cqrs_projector mongodb_cqrs
```

#### 2. Créer une Commande
```bash
curl -X POST http://localhost:8000/cqrs/commands/orders \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": 123,
    "product_id": 456, 
    "quantity": 2
  }'
```

#### 3. Interroger les Données
```bash
# Détails d'une commande
curl http://localhost:8000/cqrs/queries/orders/{order_id}

# Commandes d'un utilisateur
curl http://localhost:8000/cqrs/queries/users/123/orders

# Inventaire
curl http://localhost:8000/cqrs/queries/inventory

# Statistiques
curl http://localhost:8000/cqrs/queries/statistics/orders
```

#### 4. Exécuter la Démo
```bash
cd microservices/cqrs
pip install aiohttp
python demo_cqrs.py
```

### ✅ Avantages du CQRS

1. **Performance**: Read Models optimisés pour chaque type de requête
2. **Scalabilité**: Scaling indépendant des sides Command et Query
3. **Flexibilité**: Modèles de données adaptés aux besoins spécifiques
4. **Auditabilité**: Timeline complète des events pour chaque entité
5. **Analytics**: Aggregations et statistiques précalculées
6. **Disponibilité**: Queries disponibles même si Commands sont indisponibles

### 🔍 Monitoring

- **Command Service Health**: `GET /cqrs/commands/health`
- **Query Service Health**: `GET /cqrs/queries/health`  
- **MongoDB CQRS**: Port 27018
- **RabbitMQ Management**: http://localhost:15672 (admin/admin)

### 🧪 Tests

Le script `demo_cqrs.py` démontre:
- Séparation Command/Query
- Projection d'events en temps réel
- Requêtes optimisées sur Read Models
- Analytics et statistiques
- Timeline des events par entité

Cette implémentation illustre parfaitement les concepts CQRS avec Event Broker pour le Lab 7! 🎓
