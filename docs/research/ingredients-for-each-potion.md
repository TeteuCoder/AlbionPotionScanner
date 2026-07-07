# **Global Observations**

## **Craft Yield Rules**

* **Poções Clássicas (Classic Potions):** Rendimento base de 5 unidades por cada ação de fabricação.  
* **Poções de Rastreamento (Tracking Potions / Introduzidas no *Wild Blood*):** Rendimento base de 10 unidades por cada ação de fabricação.

## **Terminology**

* **Category:** Define o agrupamento mecânico e o rendimento base da poção (Poções Clássicas ou Poções de Rastreamento).  
* **Family:** Define a finalidade ou tipo da poção (ex: Healing, Energy, Berserk).  
* **Tier:** Nível do item, extraído do prefixo do Item ID (ex: T4 \= Tier 4).

## **Data Notes**

* Esta base de dados funciona como Single Source of Truth (SSOT) para alimentar a arquitetura JSON do AlbionPotionScanner.  
* Qualquer dado desconhecido ou não especificado na pesquisa original foi marcado com a flag **TODO** para evitar suposições.

# **Validation & Inconsistencies Report**

A validação estrutural identificou as seguintes inconsistências nos dados que requerem preenchimento futuro:

* **Resolvido:** A receita T4\_POTION\_BERSERK usa Rugged Werewolf Fangs e Crenellated Burdock.  
* **Inconsistência de Nomenclatura (Aviso):** As famílias conceituais divergem dos seus respectivos Item IDs de sistema em vários casos (ex: Family "Poison Potion" usa ID COOLDOWN; Family "Invisibility Potion" usa ID CLEANSE; Family "Gigantify Potion" usa ID REVIVE). Isso foi preservado exatamente como no original.

# **Recipes**

## **Classic Potions**

### **T4\_POTION\_HEAL**

* **Item ID:** T4\_POTION\_HEAL  
* **Name:** Healing Potion  
* **Family:** Healing Potion  
* **Category:** Poções Clássicas  
* **Tier:** 4  
* **Craft Yield:** 5  
* **Ingredients:**  
  * Item ID: T4\_BURDOCK | Name: Crenellated Burdock | Quantity: 24  
  * Item ID: T3\_EGG | Name: Hen Eggs | Quantity: 6

### **T6\_POTION\_HEAL**

* **Item ID:** T6\_POTION\_HEAL  
* **Name:** Major Healing Potion  
* **Family:** Healing Potion  
* **Category:** Poções Clássicas  
* **Tier:** 6  
* **Craft Yield:** 5  
* **Ingredients:**  
  * Item ID: T6\_FOXGLOVE | Name: Elusive Foxglove | Quantity: 72  
  * Item ID: T5\_EGG | Name: Goose Eggs | Quantity: 18  
  * Item ID: T6\_ALCOHOL | Name: Potato Schnapps | Quantity: 18

### **T4\_POTION\_ENERGY**

* **Item ID:** T4\_POTION\_ENERGY  
* **Name:** Energy Potion  
* **Family:** Energy Potion  
* **Category:** Poções Clássicas  
* **Tier:** 4  
* **Craft Yield:** 5  
* **Ingredients:**  
  * Item ID: T4\_BURDOCK | Name: Crenellated Burdock | Quantity: 24  
  * Item ID: T4\_MILK | Name: Goat's Milk | Quantity: 6

### **T6\_POTION\_ENERGY**

* **Item ID:** T6\_POTION\_ENERGY  
* **Name:** Major Energy Potion  
* **Family:** Energy Potion  
* **Category:** Poções Clássicas  
* **Tier:** 6  
* **Craft Yield:** 5  
* **Ingredients:**  
  * Item ID: T6\_FOXGLOVE | Name: Elusive Foxglove | Quantity: 72  
  * Item ID: T6\_MILK | Name: Sheep's Milk | Quantity: 18  
  * Item ID: T6\_ALCOHOL | Name: Potato Schnapps | Quantity: 18

### **T5\_POTION\_REVIVE**

* **Item ID:** T5\_POTION\_REVIVE  
* **Name:** Gigantify Potion  
* **Family:** Gigantify Potion  
* **Category:** Poções Clássicas  
* **Tier:** 5  
* **Craft Yield:** 5  
* **Ingredients:**  
  * Item ID: T5\_TEASEL | Name: Dragon Teasel | Quantity: 24  
  * Item ID: T4\_BURDOCK | Name: Crenellated Burdock | Quantity: 12  
  * Item ID: T5\_EGG | Name: Goose Eggs | Quantity: 6

### **T7\_POTION\_REVIVE**

* **Item ID:** T7\_POTION\_REVIVE  
* **Name:** Major Gigantify Potion  
* **Family:** Gigantify Potion  
* **Category:** Poções Clássicas  
* **Tier:** 7  
* **Craft Yield:** 5  
* **Ingredients:**  
  * Item ID: T7\_MULLEIN | Name: Firetouched Mullein | Quantity: 72  
  * Item ID: T6\_FOXGLOVE | Name: Elusive Foxglove | Quantity: 36  
  * Item ID: T5\_EGG | Name: Goose Eggs | Quantity: 18  
  * Item ID: T7\_ALCOHOL | Name: Corn Hooch | Quantity: 18

### **T5\_POTION\_STONESKIN**

* **Item ID:** T5\_POTION\_STONESKIN  
* **Name:** Resistance Potion  
* **Family:** Resistance Potion  
* **Category:** Poções Clássicas  
* **Tier:** 5  
* **Craft Yield:** 5  
* **Ingredients:**  
  * Item ID: T5\_TEASEL | Name: Dragon Teasel | Quantity: 24  
  * Item ID: T4\_BURDOCK | Name: Crenellated Burdock | Quantity: 12  
  * Item ID: T4\_MILK | Name: Goat's Milk | Quantity: 6

### **T7\_POTION\_STONESKIN**

* **Item ID:** T7\_POTION\_STONESKIN  
* **Name:** Major Resistance Potion  
* **Family:** Resistance Potion  
* **Category:** Poções Clássicas  
* **Tier:** 7  
* **Craft Yield:** 5  
* **Ingredients:**  
  * Item ID: T7\_MULLEIN | Name: Firetouched Mullein | Quantity: 72  
  * Item ID: T6\_FOXGLOVE | Name: Elusive Foxglove | Quantity: 36  
  * Item ID: T4\_BURDOCK | Name: Crenellated Burdock | Quantity: 36  
  * Item ID: T6\_MILK | Name: Sheep's Milk | Quantity: 18  
  * Item ID: T7\_ALCOHOL | Name: Corn Hooch | Quantity: 18

### **T5\_POTION\_SLOWFIELD**

* **Item ID:** T5\_POTION\_SLOWFIELD  
* **Name:** Sticky Potion  
* **Family:** Sticky Potion  
* **Category:** Poções Clássicas  
* **Tier:** 5  
* **Craft Yield:** 5  
* **Ingredients:**  
  * Item ID: T5\_TEASEL | Name: Dragon Teasel | Quantity: 24  
  * Item ID: T4\_BURDOCK | Name: Crenellated Burdock | Quantity: 12  
  * Item ID: T4\_MILK | Name: Goat's Milk | Quantity: 6

### **T7\_POTION\_SLOWFIELD**

* **Item ID:** T7\_POTION\_SLOWFIELD  
* **Name:** Major Sticky Potion  
* **Family:** Sticky Potion  
* **Category:** Poções Clássicas  
* **Tier:** 7  
* **Craft Yield:** 5  
* **Ingredients:**  
  * Item ID: T7\_MULLEIN | Name: Firetouched Mullein | Quantity: 72  
  * Item ID: T6\_FOXGLOVE | Name: Elusive Foxglove | Quantity: 36  
  * Item ID: T4\_BURDOCK | Name: Crenellated Burdock | Quantity: 36  
  * Item ID: T5\_EGG | Name: Goose Eggs | Quantity: 18  
  * Item ID: T7\_ALCOHOL | Name: Corn Hooch | Quantity: 18

### **T4\_POTION\_COOLDOWN**

* **Item ID:** T4\_POTION\_COOLDOWN  
* **Name:** Minor Poison Potion  
* **Family:** Poison Potion  
* **Category:** Poções Clássicas  
* **Tier:** 4  
* **Craft Yield:** 5  
* **Ingredients:**  
  * Item ID: T4\_BURDOCK | Name: Crenellated Burdock | Quantity: 8  
  * Item ID: T3\_COMFREY | Name: Brightleaf Comfrey | Quantity: 4

### **T6\_POTION\_COOLDOWN**

* **Item ID:** T6\_POTION\_COOLDOWN  
* **Name:** Poison Potion  
* **Family:** Poison Potion  
* **Category:** Poções Clássicas  
* **Tier:** 6  
* **Craft Yield:** 5  
* **Ingredients:**  
  * Item ID: T6\_FOXGLOVE | Name: Elusive Foxglove | Quantity: 24  
  * Item ID: T5\_TEASEL | Name: Dragon Teasel | Quantity: 12  
  * Item ID: T3\_COMFREY | Name: Brightleaf Comfrey | Quantity: 12  
  * Item ID: T6\_MILK | Name: Sheep's Milk | Quantity: 6

### **T8\_POTION\_COOLDOWN**

* **Item ID:** T8\_POTION\_COOLDOWN  
* **Name:** Major Poison Potion  
* **Family:** Poison Potion  
* **Category:** Poções Clássicas  
* **Tier:** 8  
* **Craft Yield:** 5  
* **Ingredients:**  
  * Item ID: T8\_YARROW | Name: Ghoul Yarrow | Quantity: 72  
  * Item ID: T7\_MULLEIN | Name: Firetouched Mullein | Quantity: 36  
  * Item ID: T5\_TEASEL | Name: Dragon Teasel | Quantity: 36  
  * Item ID: T8\_MILK | Name: Cow's Milk | Quantity: 18  
  * Item ID: T8\_ALCOHOL | Name: Pumpkin Moonshine | Quantity: 18

### **T8\_POTION\_CLEANSE**

* **Item ID:** T8\_POTION\_CLEANSE  
* **Name:** Invisibility Potion  
* **Family:** Invisibility Potion  
* **Category:** Poções Clássicas  
* **Tier:** 8  
* **Craft Yield:** 5  
* **Ingredients:**  
  * Item ID: T8\_YARROW | Name: Ghoul Yarrow | Quantity: 72  
  * Item ID: T7\_MULLEIN | Name: Firetouched Mullein | Quantity: 36  
  * Item ID: T5\_TEASEL | Name: Dragon Teasel | Quantity: 36  
  * Item ID: T8\_MILK | Name: Cow's Milk | Quantity: 18  
  * Item ID: T8\_ALCOHOL | Name: Pumpkin Moonshine | Quantity: 18

## **Tracking Potions**

### **T5\_POTION\_MOB\_RESET**

* **Item ID:** T5\_POTION\_MOB\_RESET  
* **Name:** Calming Potion  
* **Family:** Calming Potion  
* **Category:** Poções de Rastreamento  
* **Tier:** 5  
* **Craft Yield:** 10  
* **Ingredients:**  
  * Item ID: T5\_ALCHEMY\_RARE\_PANTHER | Name: Fine Shadow Claws | Quantity: 1  
  * Item ID: T5\_TEASEL | Name: Dragon Teasel | Quantity: 48  
  * Item ID: T4\_BURDOCK | Name: Crenellated Burdock | Quantity: 24  
  * Item ID: T2\_AGARIC | Name: Arcane Agaric | Quantity: 12

### **T7\_POTION\_MOB\_RESET**

* **Item ID:** T7\_POTION\_MOB\_RESET  
* **Name:** Major Calming Potion  
* **Family:** Calming Potion  
* **Category:** Poções de Rastreamento  
* **Tier:** 7  
* **Craft Yield:** 10  
* **Ingredients:**  
  * Item ID: T7\_ALCHEMY\_RARE\_PANTHER | Name: Excellent Shadow Claws | Quantity: 1  
  * Item ID: T7\_MULLEIN | Name: Firetouched Mullein | Quantity: 144  
  * Item ID: T6\_FOXGLOVE | Name: Elusive Foxglove | Quantity: 72  
  * Item ID: T3\_COMFREY | Name: Brightleaf Comfrey | Quantity: 72  
  * Item ID: T2\_AGARIC | Name: Arcane Agaric | Quantity: 36  
  * Item ID: T7\_ALCOHOL | Name: Corn Hooch | Quantity: 36

### **T5\_POTION\_CLEANSE2**

* **Item ID:** T5\_POTION\_CLEANSE2  
* **Name:** Cleansing Potion  
* **Family:** Cleansing Potion  
* **Category:** Poções de Rastreamento  
* **Tier:** 5  
* **Craft Yield:** 10  
* **Ingredients:**  
  * Item ID: T5\_ALCHEMY\_RARE\_ENT | Name: Fine Sylvian Root | Quantity: 1  
  * Item ID: T5\_TEASEL | Name: Dragon Teasel | Quantity: 48  
  * Item ID: T3\_COMFREY | Name: Brightleaf Comfrey | Quantity: 24  
  * Item ID: T4\_BUTTER | Name: Goat's Butter | Quantity: 12

### **T7\_POTION\_CLEANSE2**

* **Item ID:** T7\_POTION\_CLEANSE2  
* **Name:** Major Cleansing Potion  
* **Family:** Cleansing Potion  
* **Category:** Poções de Rastreamento  
* **Tier:** 7  
* **Craft Yield:** 10  
* **Ingredients:**  
  * Item ID: T7\_ALCHEMY\_RARE\_ENT | Name: Excellent Sylvian Root | Quantity: 1  
  * Item ID: T7\_MULLEIN | Name: Firetouched Mullein | Quantity: 144  
  * Item ID: T4\_BURDOCK | Name: Crenellated Burdock | Quantity: 72  
  * Item ID: T3\_COMFREY | Name: Brightleaf Comfrey | Quantity: 72  
  * Item ID: T6\_BUTTER | Name: Sheep's Butter | Quantity: 36  
  * Item ID: T7\_ALCOHOL | Name: Corn Hooch | Quantity: 36

### **T5\_POTION\_ACID**

* **Item ID:** T5\_POTION\_ACID  
* **Name:** Acid Potion  
* **Family:** Acid Potion  
* **Category:** Poções de Rastreamento  
* **Tier:** 5  
* **Craft Yield:** 10  
* **Ingredients:**  
  * Item ID: T5\_ALCHEMY\_RARE\_DIREBEAR | Name: Fine Spirit Paws | Quantity: 1  
  * Item ID: T5\_TEASEL | Name: Dragon Teasel | Quantity: 48  
  * Item ID: T4\_BURDOCK | Name: Crenellated Burdock | Quantity: 24  
  * Item ID: T4\_MILK | Name: Goat's Milk | Quantity: 12

### **T7\_POTION\_ACID**

* **Item ID:** T7\_POTION\_ACID  
* **Name:** Major Acid Potion  
* **Family:** Acid Potion  
* **Category:** Poções de Rastreamento  
* **Tier:** 7  
* **Craft Yield:** 10  
* **Ingredients:**  
  * Item ID: T7\_ALCHEMY\_RARE\_DIREBEAR | Name: Excellent Spirit Paws | Quantity: 1  
  * Item ID: T7\_MULLEIN | Name: Firetouched Mullein | Quantity: 144  
  * Item ID: T6\_FOXGLOVE | Name: Elusive Foxglove | Quantity: 72  
  * Item ID: T6\_ALCOHOL | Name: Potato Schnapps | Quantity: 72  
  * Item ID: T6\_MILK | Name: Sheep's Milk | Quantity: 36  
  * Item ID: T7\_ALCOHOL | Name: Corn Hooch | Quantity: 36

### **T4\_POTION\_BERSERK**

* **Item ID:** T4\_POTION\_BERSERK  
* **Name:** Minor Berserk Potion  
* **Family:** Berserk Potion  
* **Category:** Poções de Rastreamento  
* **Tier:** 4  
* **Craft Yield:** 10  
* **Ingredients:**  
  * Item ID: T3\_ALCHEMY\_RARE\_WEREWOLF | Name: Rugged Werewolf Fangs | Quantity: 1  
  * Item ID: T4\_BURDOCK | Name: Crenellated Burdock | Quantity: 16

### **T6\_POTION\_BERSERK**

* **Item ID:** T6\_POTION\_BERSERK  
* **Name:** Berserk Potion  
* **Family:** Berserk Potion  
* **Category:** Poções de Rastreamento  
* **Tier:** 6  
* **Craft Yield:** 10  
* **Ingredients:**  
  * Item ID: T5\_ALCHEMY\_RARE\_WEREWOLF | Name: Fine Werewolf Fangs | Quantity: 1  
  * Item ID: T6\_FOXGLOVE | Name: Elusive Foxglove | Quantity: 48  
  * Item ID: T2\_AGARIC | Name: Arcane Agaric | Quantity: 24  
  * Item ID: T6\_ALCOHOL | Name: Potato Schnapps | Quantity: 12

### **T8\_POTION\_BERSERK**

* **Item ID:** T8\_POTION\_BERSERK  
* **Name:** Major Berserk Potion  
* **Family:** Berserk Potion  
* **Category:** Poções de Rastreamento  
* **Tier:** 8  
* **Craft Yield:** 10  
* **Ingredients:**  
  * Item ID: T7\_ALCHEMY\_RARE\_WEREWOLF | Name: Excellent Werewolf Fangs | Quantity: 1  
  * Item ID: T8\_YARROW | Name: Ghoul Yarrow | Quantity: 144  
  * Item ID: T3\_COMFREY | Name: Brightleaf Comfrey | Quantity: 72  
  * Item ID: T6\_ALCOHOL | Name: Potato Schnapps | Quantity: 72  
  * Item ID: T7\_ALCOHOL | Name: Corn Hooch | Quantity: 36  
  * Item ID: T8\_ALCOHOL | Name: Pumpkin Moonshine | Quantity: 36

### **T4\_POTION\_LAVA**

* **Item ID:** T4\_POTION\_LAVA  
* **Name:** Minor Hellfire Potion  
* **Family:** Hellfire Potion  
* **Category:** Poções de Rastreamento  
* **Tier:** 4  
* **Craft Yield:** 10  
* **Ingredients:**  
  * Item ID: T3\_ALCHEMY\_RARE\_IMP | Name: Rugged Imp's Horn | Quantity: 1  
  * Item ID: T4\_MILK | Name: Goat's Milk | Quantity: 16

### **T6\_POTION\_LAVA**

* **Item ID:** T6\_POTION\_LAVA  
* **Name:** Hellfire Potion  
* **Family:** Hellfire Potion  
* **Category:** Poções de Rastreamento  
* **Tier:** 6  
* **Craft Yield:** 10  
* **Ingredients:**  
  * Item ID: T5\_ALCHEMY\_RARE\_IMP | Name: Fine Imp's Horn | Quantity: 1  
  * Item ID: T6\_MILK | Name: Sheep's Milk | Quantity: 48  
  * Item ID: T6\_FOXGLOVE | Name: Elusive Foxglove | Quantity: 24  
  * Item ID: T3\_EGG | Name: Hen Eggs | Quantity: 12

### **T8\_POTION\_LAVA**

* **Item ID:** T8\_POTION\_LAVA  
* **Name:** Major Hellfire Potion  
* **Family:** Hellfire Potion  
* **Category:** Poções de Rastreamento  
* **Tier:** 8  
* **Craft Yield:** 10  
* **Ingredients:**  
  * Item ID: T7\_ALCHEMY\_RARE\_IMP | Name: Excellent Imp's Horn | Quantity: 1  
  * Item ID: T8\_MILK | Name: Cow's Milk | Quantity: 144  
  * Item ID: T8\_YARROW | Name: Ghoul Yarrow | Quantity: 72  
  * Item ID: T7\_MULLEIN | Name: Firetouched Mullein | Quantity: 72  
  * Item ID: T5\_EGG | Name: Goose Eggs | Quantity: 36  
  * Item ID: T8\_ALCOHOL | Name: Pumpkin Moonshine | Quantity: 36

### **T4\_POTION\_GATHER**

* **Item ID:** T4\_POTION\_GATHER  
* **Name:** Minor Gathering Potion  
* **Family:** Gathering Potion  
* **Category:** Poções de Rastreamento  
* **Tier:** 4  
* **Craft Yield:** 10  
* **Ingredients:**  
  * Item ID: T3\_ALCHEMY\_RARE\_ELEMENTAL | Name: Rugged Runestone Tooth | Quantity: 1  
  * Item ID: T4\_BUTTER | Name: Goat's Butter | Quantity: 16

### **T6\_POTION\_GATHER**

* **Item ID:** T6\_POTION\_GATHER  
* **Name:** Gathering Potion  
* **Family:** Gathering Potion  
* **Category:** Poções de Rastreamento  
* **Tier:** 6  
* **Craft Yield:** 10  
* **Ingredients:**  
  * Item ID: T5\_ALCHEMY\_RARE\_ELEMENTAL | Name: Fine Runestone Tooth | Quantity: 1  
  * Item ID: T6\_BUTTER | Name: Sheep's Butter | Quantity: 48  
  * Item ID: T6\_FOXGLOVE | Name: Elusive Foxglove | Quantity: 24  
  * Item ID: T5\_TEASEL | Name: Dragon Teasel | Quantity: 12

### **T8\_POTION\_GATHER**

* **Item ID:** T8\_POTION\_GATHER  
* **Name:** Major Gathering Potion  
* **Family:** Gathering Potion  
* **Category:** Poções de Rastreamento  
* **Tier:** 8  
* **Craft Yield:** 10  
* **Ingredients:**  
  * Item ID: T7\_ALCHEMY\_RARE\_ELEMENTAL | Name: Excellent Runestone Tooth | Quantity: 1  
  * Item ID: T8\_BUTTER | Name: Cow's Butter | Quantity: 144  
  * Item ID: T8\_YARROW | Name: Ghoul Yarrow | Quantity: 72  
  * Item ID: T7\_MULLEIN | Name: Firetouched Mullein | Quantity: 72  
  * Item ID: T6\_FOXGLOVE | Name: Elusive Foxglove | Quantity: 36  
  * Item ID: T8\_ALCOHOL | Name: Pumpkin Moonshine | Quantity: 36

### **T4\_POTION\_TORNADO**

* **Item ID:** T4\_POTION\_TORNADO  
* **Name:** Minor Tornado in a Bottle  
* **Family:** Tornado in a Bottle  
* **Category:** Poções de Rastreamento  
* **Tier:** 4  
* **Craft Yield:** 10  
* **Ingredients:**  
  * Item ID: T3\_ALCHEMY\_RARE\_EAGLE | Name: Rugged Dawnfeather | Quantity: 1  
  * Item ID: T4\_BURDOCK | Name: Crenellated Burdock | Quantity: 16

### **T6\_POTION\_TORNADO**

* **Item ID:** T6\_POTION\_TORNADO  
* **Name:** Tornado in a Bottle  
* **Family:** Tornado in a Bottle  
* **Category:** Poções de Rastreamento  
* **Tier:** 6  
* **Craft Yield:** 10  
* **Ingredients:**  
  * Item ID: T5\_ALCHEMY\_RARE\_EAGLE | Name: Fine Dawnfeather | Quantity: 1  
  * Item ID: T6\_FOXGLOVE | Name: Elusive Foxglove | Quantity: 48  
  * Item ID: T5\_TEASEL | Name: Dragon Teasel | Quantity: 24  
  * Item ID: T3\_EGG | Name: Hen Eggs | Quantity: 12

### **T8\_POTION\_TORNADO**

* **Item ID:** T8\_POTION\_TORNADO  
* **Name:** Major Tornado in a Bottle  
* **Family:** Tornado in a Bottle  
* **Category:** Poções de Rastreamento  
* **Tier:** 8  
* **Craft Yield:** 10  
* **Ingredients:**  
  * Item ID: T7\_ALCHEMY\_RARE\_EAGLE | Name: Excellent Dawnfeather | Quantity: 1  
  * Item ID: T8\_YARROW | Name: Ghoul Yarrow | Quantity: 144  
  * Item ID: T7\_MULLEIN | Name: Firetouched Mullein | Quantity: 72  
  * Item ID: T7\_ALCOHOL | Name: Corn Hooch | Quantity: 72  
  * Item ID: T5\_EGG | Name: Goose Eggs | Quantity: 36  
  * Item ID: T8\_ALCOHOL | Name: Pumpkin Moonshine | Quantity: 36
