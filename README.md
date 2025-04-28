# Convertor de Expresii Regulate în DFA

## Structura Proiectului

Proiectul constă din următoarele componente:

-   **main.py**: Script-ul Python principal care conține toată implementarea
-   **tests.json**: Fișier JSON care conține cazuri de test pentru validare

Implementarea urmează acești pași logici:

1. Parsarea expresiilor regulate și conversia în notație postfixată
2. Conversia expresiilor postfixate în Automate Finite Nedeterministe (NFA)
3. Conversia NFA în DFA
4. Simularea DFA-ului rezultat pentru a verifica dacă un șir este acceptat

## Cum se rulează

1. Asigurați-vă că aveți Python 3.x instalat
2. Plasați cazurile de test în `tests.json` urmând formatul descris mai jos
3. Rulați programul:

```bash
python main.py
```

## Detalii de Implementare

### 1. Parsarea Expresiilor și Conversia în Postfix

Implementarea suportă următorii operatori:

-   `*`: zero sau mai multe repetiții
-   `+`: una sau mai multe repetiții
-   `?`: opțional (zero sau o apariție)
-   `|`: alternare
-   `.`: concatenare (implicită între operanzi adiacenți)

Conversia în notație postfixată este realizată folosind algoritmul Shunting-Yard (implementat în funcția `Postfix()`), care gestionează precedența operatorilor.

### 2. Construcția NFA (Algoritmul lui Thompson)

Funcția `makeNFA()` implementează algoritmul de construcție al lui Thompson, care construiește un NFA dintr-o expresie regulată postfixată. Aspecte cheie:

-   Fiecare stare din NFA este reprezentată printr-un dicționar cu un ID, tabel de tranziții și tranziții lambda
-   Algoritmul procesează fiecare caracter din expresia postfixată și construiește sub-automate pentru fiecare operator


### 3. Conversia NFA în DFA (Subset construction)

Funcția `makeDFA()` implementează algoritmul Subset construction:

-   Fiecare stare din DFA reprezintă o mulțime de stări NFA
-   Algoritmul folosește starile lambda pentru a determina toate stările accesibile fără consumarea intrării
-   Tranzițiile DFA sunt construite urmărind tranzițiile posibile ale NFA-ului din fiecare set de stări

### 4. Simularea DFA

Funcția `checkStringDFA()` simulează DFA-ul pe un șir de intrare dat:

-   Urmărește starea curentă pe măsură ce procesează fiecare caracter
-   Dacă ajunge vreodată într-o stare fără tranziție validă pentru intrarea curentă, respinge șirul
-   Acceptă șirul dacă starea finală este o stare de acceptare

## Decizii de Proiectare

1. **Reprezentarea Automatelor**:

    - Am folosit clase dedicate (`NFA` și `DFA`) pentru a organiza componentele automatelor
    - Fiecare clasă conține cele 5 componente esențiale: mulțimea stărilor (Q), alfabetul (SIGMA), starea inițială (q0), stările finale (F) și funcția de tranziție (D)
    - Această abordare oferă o structurare clară a datelor și facilitează transferul informațiilor între etapele de procesare

2. **Structuri de Date**:

    - Am ales să folosesc mulțimi (`set`) pentru reprezentarea stărilor, alfabetului și stărilor finale pentru a elimina automat duplicatele
    - Funcția de tranziție este implementată ca un dicționar de dicționare (`D[stare][simbol] = [stări_următoare]`), permițând accesul rapid la tranzițiile disponibile
    - Pentru DFA, am folosit `frozenset` ca reprezentare a stărilor compuse din mai multe stări NFA, deoarece acestea trebuie să fie hashabile pentru a servi drept chei în dicționare

3. **Crearea și Manipularea Stărilor**:

    - Funcția `new_state()` generează stări cu ID-uri unice incrementale, folosind o variabilă globală `id_ct`
    - Fiecare stare este un dicționar cu trei componente:
        - `id`: identificator unic
        - `delta`: dicționar pentru tranziții cu simboluri
        - `lambda`: listă pentru tranziții lambda 
    - Această structură flexibilă permite construirea incrementală a automatelor în timpul aplicării algoritmului lui Thompson

4. **Algoritmi**:
    - Pentru conversia expresiei regulate în forma postfixată, am implementat algoritmul Shunting-Yard cu adaptări pentru operatorii specifici expresiilor regulate
    - Funcția `addOp()` inserează operatorul de concatenare (`.`) implicit între operanzi adiacenți, simplificând manipularea expresiilor
