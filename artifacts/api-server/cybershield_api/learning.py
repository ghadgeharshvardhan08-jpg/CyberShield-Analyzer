"""Original, static educational material and quiz answer keys."""

from __future__ import annotations

LESSONS: list[dict] = [
    {
        "slug": "phishing",
        "title": "Recognize phishing",
        "topic": "Phishing",
        "summary": "Spot deceptive messages before they lead you to a fake sign-in page.",
        "minutes": 6,
        "sections": [
            {
                "heading": "Slow down urgent requests",
                "body": "Phishing messages imitate an organization or person and try to make you act before checking. Unexpected warnings about account closure, payment, or delivery deserve a pause—even when the logo and writing look convincing.",
                "key_takeaway": "Urgency is a reason to verify, not a reason to rush.",
            },
            {
                "heading": "Check the destination",
                "body": "Read the hostname from right to left. In login.example.attacker.test, the registered-looking destination is attacker.test—not example.attacker.test. A familiar brand word in a subdomain does not make the site official.",
                "key_takeaway": "Open a new tab and type a known address rather than following an unexpected sign-in link.",
            },
            {
                "heading": "Verify out of band",
                "body": "Use a phone number, app, or bookmark you already trust. Do not reply to the suspicious message to ask whether it is real; a convincing sender name can be forged.",
                "key_takeaway": "Use a separate, trusted channel to confirm sensitive requests.",
            },
        ],
        "questions": [
            {
                "id": "p1",
                "prompt": "A delivery text says your parcel will be returned in ten minutes unless you sign in. What is the best first step?",
                "options": [
                    "Tap quickly so the parcel is not lost",
                    "Open the carrier's official app or type its known address yourself",
                    "Reply with your tracking number and password",
                ],
                "correct": 1,
                "explanation": "A separately opened official app or known address avoids the unexpected link and lets you verify whether the message matches a real shipment.",
            },
            {
                "id": "p2",
                "prompt": "What does the hostname account.example.attacker.test tell you?",
                "options": [
                    "It belongs to example because that word appears in the address",
                    "It is necessarily a secure subdomain",
                    "The controlling destination is attacker.test",
                ],
                "correct": 2,
                "explanation": "The important domain is near the end of the hostname. Earlier words can be chosen by whoever controls attacker.test.",
            },
            {
                "id": "p3",
                "prompt": "A message from your manager requests an urgent gift-card purchase. What should you do?",
                "options": [
                    "Confirm through a separate, known contact method",
                    "Follow the instructions because the display name is familiar",
                    "Send a small amount to test the request",
                ],
                "correct": 0,
                "explanation": "Sender names can be spoofed or accounts compromised. Confirm an unusual payment request through a trusted, independent channel.",
            },
        ],
    },
    {
        "slug": "social-engineering",
        "title": "Understand social engineering",
        "topic": "Social engineering",
        "summary": "Recognize manipulation tactics that target trust, authority, and routine.",
        "minutes": 5,
        "sections": [
            {
                "heading": "The tactic is the signal",
                "body": "Social engineering uses human expectations—helpfulness, respect for authority, fear, curiosity, or a desire to avoid trouble—to bypass normal checks. It can happen by phone, chat, email, or in person.",
                "key_takeaway": "Judge the request and its verification, not just the person's claimed identity.",
            },
            {
                "heading": "Protect verification codes",
                "body": "One-time codes and approval prompts are security credentials. A caller who asks you to read out a code may be trying to complete a sign-in as you. Do not approve a prompt you did not initiate.",
                "key_takeaway": "Never share an authentication code with someone who contacted you.",
            },
            {
                "heading": "Use a pause-and-verify routine",
                "body": "Stop, avoid using the contact details in the request, and verify through a channel you already know. Report pressure to bypass policy rather than making an exception.",
                "key_takeaway": "A legitimate request can withstand a short verification step.",
            },
        ],
        "questions": [
            {
                "id": "s1",
                "prompt": "An unexpected caller asks you to read a sign-in code aloud. What should you do?",
                "options": ["Share it if the caller knows your name", "Do not share it and verify independently", "Send a screenshot instead"],
                "correct": 1,
                "explanation": "A one-time code can let another person complete a sign-in. Keep it private and contact the organization using a trusted number.",
            },
            {
                "id": "s2",
                "prompt": "A request says normal approval steps must be skipped because it is urgent. What is the safest response?",
                "options": ["Follow the normal process and verify the request", "Skip the process once", "Ask the requester to repeat the urgency"],
                "correct": 0,
                "explanation": "Pressure to bypass a safeguard is a reason to verify the request, not an exception to the safeguard.",
            },
            {
                "id": "s3",
                "prompt": "Which detail is strongest evidence that an unusual request is legitimate?",
                "options": ["A familiar profile picture", "A separate confirmation using a known contact route", "A message saying 'trust me'"],
                "correct": 1,
                "explanation": "A separate known channel is harder for an impersonator to control than profile pictures or claims in the same message.",
            },
        ],
    },
    {
        "slug": "password-security",
        "title": "Build stronger account security",
        "topic": "Password security",
        "summary": "Use unique passwords, a password manager, and multi-factor authentication.",
        "minutes": 5,
        "sections": [
            {
                "heading": "Make passwords unique",
                "body": "A long password or passphrase is easier to defend when it is not reused. Reuse allows a password exposed by one service to unlock another account.",
                "key_takeaway": "Use a unique password for every important account.",
            },
            {
                "heading": "Use a password manager",
                "body": "A reputable password manager can create and store random unique passwords so you do not have to memorize each one. Protect the manager with a strong master password and its available recovery controls.",
                "key_takeaway": "Do not make passwords predictable just to make them easy to remember.",
            },
            {
                "heading": "Add another factor",
                "body": "Multi-factor authentication adds a separate proof of identity. Passkeys or authenticator apps are generally more resistant to phishing than SMS codes, but any additional factor is better than password-only access.",
                "key_takeaway": "Enable MFA, and never approve a prompt you did not initiate.",
            },
        ],
        "questions": [
            {
                "id": "pw1",
                "prompt": "Why should important accounts have unique passwords?",
                "options": ["It makes typing faster", "A breach at one service should not unlock another", "It avoids needing MFA"],
                "correct": 1,
                "explanation": "Unique passwords limit the damage from credential stuffing after a password leak.",
            },
            {
                "id": "pw2",
                "prompt": "Which is a good use of a password manager?",
                "options": ["Save one password and reuse it everywhere", "Generate and store unique passwords", "Share your vault with support staff"],
                "correct": 1,
                "explanation": "Generating unique passwords is a key benefit. Keep vault access private and secure its recovery options.",
            },
            {
                "id": "pw3",
                "prompt": "You receive an MFA approval prompt you did not request. What should you do?",
                "options": ["Approve it to clear the notification", "Deny it and secure/check the account", "Share the prompt with a coworker"],
                "correct": 1,
                "explanation": "An unexpected prompt may mean someone has your password. Deny it and review the account through its official site.",
            },
        ],
    },
    {
        "slug": "ransomware",
        "title": "Prepare for ransomware",
        "topic": "Ransomware",
        "summary": "Reduce the impact of malicious file encryption and extortion.",
        "minutes": 6,
        "sections": [
            {
                "heading": "What ransomware does",
                "body": "Ransomware can encrypt files, interrupt operations, and threaten to publish stolen information. Paying does not guarantee recovery or deletion of stolen data.",
                "key_takeaway": "Prevention and tested recovery plans matter more than a promise from an attacker.",
            },
            {
                "heading": "Keep recoverable backups",
                "body": "Keep backups separated from everyday accounts and devices so malware cannot easily change or erase every copy. Test restoring a file before an incident.",
                "key_takeaway": "A backup is useful only if it is protected and can be restored.",
            },
            {
                "heading": "Respond safely",
                "body": "If a device may be infected, follow your organization's incident plan, alert security staff, and avoid connecting backup drives. Do not wipe evidence or negotiate on your own.",
                "key_takeaway": "Isolate and report suspected incidents using the established response plan.",
            },
        ],
        "questions": [
            {
                "id": "r1",
                "prompt": "What makes a backup more resilient to ransomware?",
                "options": ["It is always connected with full write access", "It is separated from everyday devices and tested", "It is stored beside the only copy"],
                "correct": 1,
                "explanation": "Separation and restore testing help preserve a recovery path if an infected device tries to encrypt or delete files.",
            },
            {
                "id": "r2",
                "prompt": "A work laptop displays a ransom note. What should you do first?",
                "options": ["Follow your incident plan and contact security staff", "Plug in all backup drives", "Install a random cleanup tool"],
                "correct": 0,
                "explanation": "Use the organization's incident response process to reduce spread and preserve evidence.",
            },
            {
                "id": "r3",
                "prompt": "Does paying a ransom guarantee the files will be restored?",
                "options": ["Yes, payment creates a guarantee", "No, recovery and deletion are not guaranteed", "Only if payment is made quickly"],
                "correct": 1,
                "explanation": "There is no reliable guarantee that attackers will restore files or delete stolen data after payment.",
            },
        ],
    },
    {
        "slug": "malware",
        "title": "Avoid common malware paths",
        "topic": "Malware",
        "summary": "Reduce risk from unexpected attachments, downloads, and software.",
        "minutes": 5,
        "sections": [
            {
                "heading": "Unexpected files deserve checks",
                "body": "Malware may arrive through attachments, fake updates, pirated software, or links that imitate familiar tools. File names and icons can be misleading.",
                "key_takeaway": "Confirm unexpected files with the sender through a different channel.",
            },
            {
                "heading": "Keep software current",
                "body": "Updates often repair known security flaws. Install updates from the operating system's or application's built-in update mechanism, not a pop-up's download link.",
                "key_takeaway": "Use official update channels and remove software you no longer need.",
            },
            {
                "heading": "Use least privilege",
                "body": "Everyday accounts should not have more permissions than necessary. A standard user account can limit the changes malicious software can make.",
                "key_takeaway": "Do not grant administrator permission unless you understand why it is needed.",
            },
        ],
        "questions": [
            {
                "id": "m1",
                "prompt": "An unexpected invoice attachment arrives from a familiar sender. What is a safe next step?",
                "options": ["Open it immediately", "Verify with the sender through a separate channel", "Disable security software first"],
                "correct": 1,
                "explanation": "The sender's account could be compromised. Verify before opening unexpected files.",
            },
            {
                "id": "m2",
                "prompt": "Where should you install a routine software update from?",
                "options": ["The software's built-in updater or official source", "A browser pop-up's shortened link", "A file-sharing comment"],
                "correct": 0,
                "explanation": "Official update mechanisms reduce the chance of downloading a fake installer.",
            },
            {
                "id": "m3",
                "prompt": "Why use a standard account for everyday work?",
                "options": ["It prevents all malware", "It limits unnecessary privileges", "It makes every attachment safe"],
                "correct": 1,
                "explanation": "Least privilege can reduce the impact of malicious software, though it cannot prevent every infection.",
            },
        ],
    },
    {
        "slug": "safe-browsing",
        "title": "Browse with care",
        "topic": "Safe browsing",
        "summary": "Check destinations, limit data sharing, and treat browser warnings seriously.",
        "minutes": 5,
        "sections": [
            {
                "heading": "HTTPS is necessary, not proof",
                "body": "HTTPS encrypts traffic between your browser and a site. It does not prove the site is honest, professionally run, or free of malware.",
                "key_takeaway": "A lock icon protects the connection; it does not endorse the destination.",
            },
            {
                "heading": "Pause on browser warnings",
                "body": "A browser warning may indicate a certificate, download, or known-reputation problem. Do not bypass it to reach an important account; use a trusted address and investigate.",
                "key_takeaway": "Do not bypass security warnings just because a page looks familiar.",
            },
            {
                "heading": "Share less",
                "body": "Avoid putting passwords, one-time codes, identity documents, or payment details into a page unless you verified the exact destination and the request is expected.",
                "key_takeaway": "Check the address and purpose before entering sensitive information.",
            },
        ],
        "questions": [
            {
                "id": "b1",
                "prompt": "What does HTTPS tell you?",
                "options": ["The site is definitely legitimate", "The connection is encrypted, but the site may still be deceptive", "The site has no malware"],
                "correct": 1,
                "explanation": "HTTPS protects data in transit; it does not establish the site owner's trustworthiness.",
            },
            {
                "id": "b2",
                "prompt": "A browser warns that a sign-in site may be unsafe. What is the best response?",
                "options": ["Bypass the warning because the logo looks right", "Use a trusted bookmark or official app and investigate", "Enter a fake password to test it"],
                "correct": 1,
                "explanation": "A trusted route avoids bypassing a warning or sharing credentials with a possibly deceptive page.",
            },
            {
                "id": "b3",
                "prompt": "When should you enter a one-time code into a web page?",
                "options": ["Only after independently verifying the destination and initiating the sign-in", "Whenever the page requests it", "After forwarding it to the sender"],
                "correct": 0,
                "explanation": "Codes should only be entered into a verified service during a sign-in you initiated.",
            },
        ],
    },
]


def get_lesson(slug: str) -> dict | None:
    return next((lesson for lesson in LESSONS if lesson["slug"] == slug), None)


def public_lesson(lesson: dict, progress: dict | None = None) -> dict:
    progress = progress or {}
    return {
        "slug": lesson["slug"],
        "title": lesson["title"],
        "topic": lesson["topic"],
        "summary": lesson["summary"],
        "minutes": lesson["minutes"],
        "sections": lesson["sections"],
        "questions": [
            {
                "id": question["id"],
                "prompt": question["prompt"],
                "options": [
                    {"label": chr(65 + i), "text": option}
                    for i, option in enumerate(question["options"])
                ],
            }
            for question in lesson["questions"]
        ],
        "completed": bool(progress.get("completed", False)),
        "best_score": progress.get("best_score"),
    }


def public_lesson_summary(lesson: dict, progress: dict | None = None) -> dict:
    progress = progress or {}
    return {
        "slug": lesson["slug"],
        "title": lesson["title"],
        "topic": lesson["topic"],
        "summary": lesson["summary"],
        "minutes": lesson["minutes"],
        "completed": bool(progress.get("completed", False)),
        "best_score": progress.get("best_score"),
    }
