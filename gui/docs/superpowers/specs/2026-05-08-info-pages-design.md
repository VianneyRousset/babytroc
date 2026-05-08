# Info Pages Design — /me/about, /me/faq, /me/politics, /me/contact

## Context

Babytroc is a lausannoise platform for lending and borrowing children's items between individuals. Four stub pages exist under `/me/` with placeholder "In construction" content. They are already linked from the `/me` menu (Info section). This spec replaces the placeholders with real French content.

## Shared Pattern

All four pages follow the existing pattern:
- `definePageMeta({ layout: 'me', appBack: true, appTitle: '...' })`
- `<AppPage>` wrapping `<Panel>` with static content
- No new dependencies or components (except `<details>/<summary>` for FAQ)
- Existing form components (`TextInput`, `LongTextInput`, `TextButton`) used for the contact form
- Max width constrained via `<AppPage :max-width="600">`

## Page 1: A propos (`/me/about`)

**Title:** A propos

**Sections:**

1. **Hero** — `<PanelBanner>` with app name "Babytroc" and tagline: "La plateforme lausannoise de pret d'articles pour enfants entre particuliers."

2. **Notre mission** — Short paragraph: reduce waste, build community trust, make parenting more affordable by enabling item lending between families.

3. **Comment ca marche** — Three numbered steps:
   - Publiez vos articles pour enfants que vous n'utilisez plus
   - Empruntez ce dont vous avez besoin pres de chez vous
   - Restituez l'article une fois que vous n'en avez plus besoin

4. **Nos valeurs** — Three short items:
   - Confiance: a community built on trust between parents
   - Durabilite: give items a second life instead of buying new
   - Communaute: connect local families and strengthen neighborhood ties

**Components:** `AppPage`, `Panel`, `PanelBanner`. All static text, no interactivity.

## Page 2: FAQ (`/me/faq`)

**Title:** FAQ

**Format:** Accordion-style Q&A using native `<details>/<summary>` elements, styled to match the app.

**Questions & Answers:**

1. **Qu'est-ce que Babytroc ?**
   Babytroc est une plateforme lausannoise qui permet aux parents de preter et d'emprunter des articles pour enfants entre particuliers. L'objectif est de reduire le gaspillage et de rendre la parentalite plus accessible.

2. **Comment ca marche ?**
   Creez un compte, publiez les articles que vous souhaitez preter, et parcourez les annonces pour trouver ce dont vous avez besoin. Contactez le preteur via la messagerie integree pour organiser l'emprunt.

3. **Est-ce gratuit ?**
   Oui, Babytroc est entierement gratuit. Aucun frais n'est applique pour publier une annonce ou emprunter un article.

4. **Comment creer un compte ?**
   Rendez-vous sur la page de connexion et suivez les instructions pour creer votre compte. Vous aurez besoin d'une adresse email valide.

5. **Comment contacter un preteur ?**
   Sur la page d'un article, utilisez le bouton de contact pour envoyer un message au preteur via notre messagerie integree.

6. **Que faire en cas de probleme avec un article ?**
   Contactez-nous via la page Contact. Nous ferons de notre mieux pour vous aider a resoudre la situation.

7. **Mes donnees sont-elles protegees ?**
   Oui, nous prenons la protection de vos donnees tres au serieux. Consultez notre page Politiques pour en savoir plus sur notre politique de confidentialite.

**Styling:** Each `<details>` gets a border, padding, and smooth open/close transition. Summary text is bold. Answers have normal weight and secondary text color.

**Components:** `AppPage`, `Panel`. No new components needed.

## Page 3: Contact (`/me/contact`)

**Title:** Contact

**Sections:**

1. **Intro text:** "Une question, un probleme ou une suggestion ? Contactez-nous !"

2. **Email link:** `contact@babytroc.ch` displayed as a clickable `mailto:` link.

3. **Contact form** with fields:
   - Nom (`TextInput`, placeholder: "Votre nom")
   - Email (`TextInput`, type: "email", placeholder: "Votre adresse email")
   - Sujet (`TextInput`, placeholder: "Sujet de votre message")
   - Message (`LongTextInput`, placeholder: "Votre message...")
   - Submit button (`TextButton`, aspect: "flat", color: "primary", text: "Envoyer")

4. **Form behavior (frontend-only):**
   - Basic validation: all fields required, email format check
   - On submit: show a success message ("Merci ! Votre message a bien ete envoye.") and reset the form
   - No actual backend call — purely frontend placeholder

**Components:** `AppPage`, `Panel`, `TextInput`, `LongTextInput`, `TextButton`.

## Page 4: Politiques (`/me/politics`)

**Title:** Politiques

Three sections, each with a heading and content paragraphs. Written in clear, accessible French — not legalese.

### Section 1: Conditions d'utilisation

- Babytroc est une plateforme de mise en relation entre particuliers pour le pret d'articles pour enfants
- L'utilisateur est responsable de l'exactitude des informations publiees
- Les articles proposes doivent etre en bon etat et conformes a leur description
- Babytroc n'est pas responsable des transactions entre utilisateurs
- Babytroc se reserve le droit de supprimer tout contenu ne respectant pas les regles de la communaute

### Section 2: Politique de confidentialite

- Donnees collectees: adresse email, informations de profil, donnees d'utilisation
- Utilisation: gestion du compte, communication entre utilisateurs, amelioration du service
- Partage: les donnees ne sont jamais vendues a des tiers
- Droits: l'utilisateur peut demander l'acces, la modification ou la suppression de ses donnees en nous contactant
- Securite: les donnees sont stockees de maniere securisee

### Section 3: Regles de la communaute

- Seuls les articles pour enfants sont autorises
- Les articles doivent etre propres, fonctionnels et conformes a leur description
- **Regles pour les photos:**
  - Aucune personne ne doit apparaitre sur les photos (ni adulte, ni enfant, ni bebe)
  - Eviter de montrer excessivement l'espace prive (interieur du domicile)
  - Aucun contenu a caractere sexuel, haineux ou degoutant
- La communication entre utilisateurs doit rester respectueuse et bienveillante
- Toute activite commerciale est interdite
- Le non-respect de ces regles peut entrainer la suspension ou la suppression du compte

**Components:** `AppPage`, `Panel`. All static text.
