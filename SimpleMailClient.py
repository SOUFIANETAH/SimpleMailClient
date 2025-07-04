import subprocess
import base64
import sys
import os
from datetime import datetime
import time
import threading

class SimpleMailClient:
    
    def __init__(self):
        self.smtp_server = ""
        self.smtp_port = ""
        self.pop3_server = ""
        self.pop3_port = ""
        self.imap_server = ""
        self.imap_port = ""
        self.username = ""
        self.password = ""

    def soufiane_banner(self):
        print("""
╔══════════════════════════════════════╗
║          SOUFIANE TAHIRI             ║
╚══════════════════════════════════════╝
    """)    
        
    def configure_servers(self):
        
        """Configuration des serveurs de messagerie"""
        
        print("=== Configuration des serveurs ===")
        self.smtp_server = input("Serveur SMTP (ex: smtp.gmail.com): ")
        self.smtp_port = input("Port SMTP (ex: 587 pour TLS, 465 pour SSL): ")
        self.pop3_server = input("Serveur POP3 (ex: pop.gmail.com): ")
        self.pop3_port = input("Port POP3 (ex: 995): ")
        self.imap_server = input("Serveur IMAP (ex: imap.gmail.com): ")
        self.imap_port = input("Port IMAP (ex: 993): ")
        self.username = input("Nom d'utilisateur (email): ")
        self.password = input("Mot de passe: ")
    
    def get_credentials(self):
        """Obtenir les identifiants si non configurés"""
        if not self.username:
            self.username = input("Nom d'utilisateur (email): ")
        if not self.password:
            self.password = input("Mot de passe: ")
        return bool(self.username and self.password)
        
    def execute_openssl_command(self, command, input_data):
        """Exécute une commande openssl et envoie les données"""
        try:
           
            import tempfile
            with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.txt') as f:
                f.write(input_data)
                temp_file = f.name
            
           
            full_command = f"{command} < {temp_file}"
            
            process = subprocess.Popen(
                full_command,
                shell=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            
            stdout, stderr = process.communicate()
            
          
            os.unlink(temp_file)
            
            return stdout, stderr
        except Exception as e:
            print(f"Erreur lors de l'exécution: {e}")
            return "", str(e)
    
    def send_email_smtp_interactive(self):
        """SMTP avec interaction temps réel - CORRIGÉ"""
        print("\n=== ENVOI EMAIL SMTP (Interactif) ===")
        
        if not self.username:
            if not self.get_credentials():
                return
                
      
        to_email = input("Destinataire: ").strip()
        subject = input("Sujet: ").strip()
        message = input("Message: ").strip()
        
        if not to_email or not subject or not message:
            print("Tous les champs requis!")
            return
            
      
        print("\n1. Gmail")
        print("2. Outlook") 
        print("3. Autre")
        choice = input("Serveur (1-3): ").strip()
        
        if choice == "1":
            server, port = "smtp.gmail.com", "587"
        elif choice == "2":
            server, port = "smtp-mail.outlook.com", "587"
        else:
            server = input("Serveur SMTP: ").strip()
            port = input("Port: ").strip()
            
        try:
            print(f"\n Connexion à {server}:{port}...")
            
           
            cmd = ['openssl', 's_client', '-connect', f'{server}:{port}', 
                   '-starttls', 'smtp', '-quiet']
            
            print(f" Commande: {' '.join(cmd)}")
            
           
            process = subprocess.Popen(cmd, 
                                     stdin=subprocess.PIPE,
                                     stdout=subprocess.PIPE,
                                     stderr=subprocess.PIPE,
                                     text=True, bufsize=0)
            
            
            print(" Attente de la connexion...")
            time.sleep(3)
            
           
            def read_output():
                try:
                    while True:
                        line = process.stdout.readline()
                        if line:
                            print(f"<< {line.strip()}")
                        else:
                            break
                except:
                    pass
            
           
            reader = threading.Thread(target=read_output, daemon=True)
            reader.start()
            
           
            auth_string = f"\x00{self.username}\x00{self.password}"
            auth_b64 = base64.b64encode(auth_string.encode()).decode()
            
            # Envoi des commandes 
            commands = [
                f"EHLO localhost",
                f"AUTH PLAIN {auth_b64}",
                f"MAIL FROM:<{self.username}>",
                f"RCPT TO:<{to_email}>",
                "DATA",
                f"From: {self.username}",
                f"To: {to_email}",
                f"Subject: {subject}",
                "",
                message,
                ".",
                "QUIT"
            ]
            
            print("\n Envoi des commandes SMTP:")
            print("=" * 40)
            
            for cmd in commands:
                print(f">> {cmd}")
                process.stdin.write(cmd + "\n")
                process.stdin.flush()
                time.sleep(1)  # Pause importante!
                
            # Attendre la fin
            time.sleep(3)
            process.terminate()
            
            print("=" * 40)
            print("Commandes SMTP envoyées!")
            
        except Exception as e:
            print(f" Erreur SMTP: {e}")
    
    def read_emails_pop3(self):
        """Lecture des emails via POP3 avec openssl"""
        print("\n=== Lecture des emails via POP3 ===")
        
        
        pop3_stat_commands = f"""USER {self.username}
PASS {self.password}
STAT
LIST
QUIT
"""
        
        openssl_cmd = f"openssl s_client -connect {self.pop3_server}:{self.pop3_port} -ign_eof"
        
        print("Récupération de la liste des messages...")
        stdout, stderr = self.execute_openssl_command(openssl_cmd, pop3_stat_commands)
        
       
        lines = stdout.split('\n')
        message_count = 0
        message_list = []
        
        for line in lines:
            if line.startswith('+OK') and 'messages' in line:
                try:
                    message_count = int(line.split()[1])
                except:
                    pass
            elif line.strip() and line[0].isdigit() and ' ' in line:
                parts = line.split()
                if len(parts) >= 2 and parts[0].isdigit():
                    message_list.append((int(parts[0]), parts[1]))
        
        print(f"\n Nombre total de messages: {message_count}")
        
        if message_count == 0:
            print("Aucun message dans la boîte de réception.")
            return
        
        print("\n--- Liste des messages ---")
        for msg_num, size in message_list:
            print(f"Message {msg_num}: {size} octets")
        
        # Demander quel message lire
        while True:
            try:
                choice = input(f"\nQuel message lire? (1-{message_count}, 0 pour quitter): ")
                if choice == "0":
                    return
                
                msg_num = int(choice)
                if 1 <= msg_num <= message_count:
                    break
                else:
                    print(f"Veuillez choisir un numéro entre 1 et {message_count}")
            except ValueError:
                print("Veuillez entrer un numéro valide")
        
        
        pop3_retr_commands = f"""USER {self.username}
PASS {self.password}
RETR {msg_num}
QUIT
"""
        
        print(f"\nRécupération du message {msg_num}...")
        stdout, stderr = self.execute_openssl_command(openssl_cmd, pop3_retr_commands)
        
        print(f"\n--- Message {msg_num} ---")
        # Extraire le contenu du message
        in_message = False
        message_content = []
        
        for line in stdout.split('\n'):
            if line.startswith('+OK') and 'octets' in line:
                in_message = True
                continue
            elif line.strip() == '.' and in_message:
                break
            elif in_message:
                message_content.append(line)
        
        if message_content:
            print('\n'.join(message_content))
        else:
            print("Contenu du message non trouvé dans la réponse")
            print("\n--- Réponse brute du serveur ---")
            print(stdout)
        
        if stderr:
            print(f"Messages système: {stderr}")
    
    def read_emails_imap(self):
        """Lecture des emails via IMAP avec openssl"""
        print("\n=== Lecture des emails via IMAP ===")
        
        
        imap_list_commands = f"""A01 LOGIN {self.username} {self.password}
A02 SELECT INBOX
A03 SEARCH ALL
A04 LOGOUT
"""
        
        openssl_cmd = f"openssl s_client -connect {self.imap_server}:{self.imap_port} -ign_eof"
        
        print("Récupération de la liste des messages...")
        stdout, stderr = self.execute_openssl_command(openssl_cmd, imap_list_commands)
        
        
        message_numbers = []
        message_count = 0
        
        for line in stdout.split('\n'):
            if 'EXISTS' in line and line.strip().startswith('*'):
                try:
                    message_count = int(line.split()[1])
                except:
                    pass
            elif line.startswith('* SEARCH'):
                
                parts = line.split()[2:]  # Ignorer "* SEARCH"
                for part in parts:
                    if part.isdigit():
                        message_numbers.append(int(part))
        
        print(f"\n Nombre total de messages: {message_count}")
        
        if message_count == 0 or not message_numbers:
            print("Aucun message dans la boîte de réception.")
            return
        
        print(f"Messages disponibles: {', '.join(map(str, message_numbers))}")
        
        # Demander quel message lire
        while True:
            try:
                choice = input(f"\nQuel message lire? ({', '.join(map(str, message_numbers))}, 0 pour quitter): ")
                if choice == "0":
                    return
                
                msg_num = int(choice)
                if msg_num in message_numbers:
                    break
                else:
                    print(f"Veuillez choisir un numéro parmi: {', '.join(map(str, message_numbers))}")
            except ValueError:
                print("Veuillez entrer un numéro valide")
        
        
        imap_fetch_commands = f"""A01 LOGIN {self.username} {self.password}
A02 SELECT INBOX
A03 FETCH {msg_num} (ENVELOPE BODY[HEADER] BODY[TEXT])
A04 LOGOUT
"""
        
        print(f"\nRécupération du message {msg_num}...")
        stdout, stderr = self.execute_openssl_command(openssl_cmd, imap_fetch_commands)
        
        print(f"\n--- Message {msg_num} ---")
        print(stdout)
        
        if stderr:
            print(f"\nMessages système: {stderr}")
    
    def show_menu(self):
        """Affiche le menu principal"""
        print("\n" + "="*50)
        print("    CLIENT DE MESSAGERIE SIMPLE")
        print("="*50)
        print("1. Configurer les serveurs")
        print("2. Envoyer un email (SMTP)")
        print("3. Lire les emails (POP3)")
        print("4. Lire les emails (IMAP)")
        print("5. Quitter")
        print("="*50)
    
    def run(self):
        """Boucle principale du programme"""
        print("Client de messagerie utilisant openssl s_client")
        print("Assurez-vous qu'openssl est installé sur votre système")

        self.soufiane_banner()
        
        while True:
            self.show_menu()
            choice = input("Votre choix (1-5): ").strip()
            
            if choice == "1":
                self.configure_servers()
            elif choice == "2":
                if not self.username:
                    print("Veuillez d'abord configurer les serveurs (option 1)")
                    continue
                self.send_email_smtp_interactive()
            elif choice == "3":
                if not self.username:
                    print("Veuillez d'abord configurer les serveurs (option 1)")
                    continue
                self.read_emails_pop3()
            elif choice == "4":
                if not self.username:
                    print("Veuillez d'abord configurer les serveurs (option 1)")
                    continue
                self.read_emails_imap()
            elif choice == "5":
                print("Au revoir!")
                sys.exit(0)
            else:
                print("Choix invalide. Veuillez choisir entre 1 et 5.")

def main():
    """Fonction principale"""
   
    try:
        subprocess.run(["openssl", "version"], capture_output=True, check=True)
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("ERREUR: openssl n'est pas installé ou accessible.")
        print("Veuillez installer openssl pour utiliser ce programme.")
        sys.exit(1)
    
    client = SimpleMailClient()
    client.run()

if __name__ == "__main__":
    main()