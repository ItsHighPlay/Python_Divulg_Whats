"""
Módulo para acessar e-mail e buscar códigos de verificação
Suporta Gmail via IMAP e Gmail API
"""
import re
import time
import imaplib
import email
from email.header import decode_header
from datetime import datetime, timedelta


class EmailHandler:
    """Classe para manipular e-mails e buscar códigos de verificação"""
    
    def __init__(self, email_address: str, password: str, provider: str = "gmail"):
        """
        Inicializa o handler de e-mail
        
        :param email_address: Endereço de e-mail
        :param password: Senha do e-mail ou App Password (Gmail)
        :param provider: Provedor de e-mail (gmail, outlook, etc)
        """
        self.email_address = email_address
        self.password = password
        self.provider = provider.lower()
        self.imap = None
        
        # Configurações IMAP por provedor
        self.imap_servers = {
            'gmail': 'imap.gmail.com',
            'outlook': 'outlook.office365.com',
            'hotmail': 'outlook.office365.com',
            'yahoo': 'imap.mail.yahoo.com',
        }
    
    def connect(self):
        """
        Conecta ao servidor IMAP
        
        :return: True se conectado com sucesso
        """
        try:
            imap_server = self.imap_servers.get(self.provider, 'imap.gmail.com')
            print(f"🔌 Conectando ao servidor IMAP: {imap_server}")
            
            self.imap = imaplib.IMAP4_SSL(imap_server)
            self.imap.login(self.email_address, self.password)
            
            print(f"✓ Conectado ao e-mail: {self.email_address}")
            return True
            
        except imaplib.IMAP4.error as e:
            print(f"✗ Erro de autenticação IMAP: {str(e)}")
            print("\n💡 Dica para Gmail:")
            print("   1. Ative 'Acesso a app menos seguro' OU")
            print("   2. Use 'Senha de app': https://myaccount.google.com/apppasswords")
            return False
        except Exception as e:
            print(f"✗ Erro ao conectar ao e-mail: {str(e)}")
            return False
    
    def disconnect(self):
        """Desconecta do servidor IMAP"""
        if self.imap:
            try:
                self.imap.close()
                self.imap.logout()
                print("✓ Desconectado do e-mail")
            except:
                pass
    
    def get_verification_code_from_mercadolivre(self, max_attempts: int = 10, wait_seconds: int = 5):
        """
        Busca código de verificação do Mercado Livre no e-mail
        
        :param max_attempts: Número máximo de tentativas
        :param wait_seconds: Segundos entre cada tentativa
        :return: Código de verificação ou None
        """
        print(f"\n📧 Buscando código de verificação no e-mail...")
        
        for attempt in range(1, max_attempts + 1):
            print(f"   Tentativa {attempt}/{max_attempts}...")
            
            try:
                # Seleciona a caixa de entrada
                self.imap.select('INBOX')
                
                # Busca e-mails recentes do Mercado Livre (últimos 5 minutos)
                # Filtra por remetente do Mercado Livre
                date_since = (datetime.now() - timedelta(minutes=5)).strftime("%d-%b-%Y")
                
                search_criteria = f'(FROM "mercadolivre" SINCE {date_since})'
                _, message_numbers = self.imap.search(None, search_criteria)
                
                if not message_numbers[0]:
                    print(f"   Nenhum e-mail encontrado. Aguardando {wait_seconds}s...")
                    time.sleep(wait_seconds)
                    continue
                
                # Pega os IDs dos e-mails
                email_ids = message_numbers[0].split()
                
                # Processa e-mails do mais recente para o mais antigo
                for email_id in reversed(email_ids):
                    _, msg_data = self.imap.fetch(email_id, '(RFC822)')
                    
                    for response_part in msg_data:
                        if isinstance(response_part, tuple):
                            msg = email.message_from_bytes(response_part[1])
                            
                            # Extrai assunto
                            subject = self._decode_subject(msg['subject'])
                            
                            # Verifica se é e-mail de verificação
                            if self._is_verification_email(subject):
                                print(f"   ✓ E-mail de verificação encontrado: {subject}")
                                
                                # Extrai código do corpo do e-mail
                                code = self._extract_code_from_email(msg)
                                
                                if code:
                                    print(f"   ✓ Código encontrado: {code}")
                                    return code
                
                print(f"   Código não encontrado. Aguardando {wait_seconds}s...")
                time.sleep(wait_seconds)
                
            except Exception as e:
                print(f"   Erro ao buscar e-mails: {str(e)}")
                time.sleep(wait_seconds)
        
        print("✗ Código de verificação não encontrado após todas as tentativas")
        return None
    
    def _decode_subject(self, subject_header):
        """Decodifica o assunto do e-mail"""
        if not subject_header:
            return ""
        
        decoded_parts = decode_header(subject_header)
        subject = ""
        
        for part, encoding in decoded_parts:
            if isinstance(part, bytes):
                subject += part.decode(encoding or 'utf-8', errors='ignore')
            else:
                subject += str(part)
        
        return subject
    
    def _is_verification_email(self, subject: str):
        """
        Verifica se o assunto indica e-mail de verificação
        
        :param subject: Assunto do e-mail
        :return: True se for e-mail de verificação
        """
        verification_keywords = [
            'código',
            'codigo',
            'verificação',
            'verificacao',
            'verification',
            'security code',
            'autenticação',
            'autenticacao',
            'confirma',
            'two-step',
            '2fa',
            'token'
        ]
        
        subject_lower = subject.lower()
        return any(keyword in subject_lower for keyword in verification_keywords)
    
    def _extract_code_from_email(self, msg):
        """
        Extrai código de verificação do corpo do e-mail
        
        :param msg: Objeto de mensagem de e-mail
        :return: Código extraído ou None
        """
        body = self._get_email_body(msg)
        
        if not body:
            return None
        
        # Padrões de regex para encontrar códigos
        # Códigos de 4 a 8 dígitos
        patterns = [
            r'\b(\d{6})\b',  # 6 dígitos (mais comum)
            r'\b(\d{4,8})\b',  # 4 a 8 dígitos
            r'código[:\s]+(\d+)',  # "código: 123456"
            r'codigo[:\s]+(\d+)',  # "codigo: 123456"
            r'code[:\s]+(\d+)',  # "code: 123456"
            r'token[:\s]+(\d+)',  # "token: 123456"
            r'verification code[:\s]+(\d+)',
        ]
        
        for pattern in patterns:
            match = re.search(pattern, body, re.IGNORECASE)
            if match:
                code = match.group(1)
                # Valida se o código tem tamanho razoável (4-8 dígitos)
                if 4 <= len(code) <= 8:
                    return code
        
        return None
    
    def _get_email_body(self, msg):
        """
        Extrai o corpo do e-mail
        
        :param msg: Objeto de mensagem
        :return: Corpo do e-mail como texto
        """
        body = ""
        
        if msg.is_multipart():
            for part in msg.walk():
                content_type = part.get_content_type()
                content_disposition = str(part.get("Content-Disposition"))
                
                # Pega apenas partes de texto
                if content_type == "text/plain" and "attachment" not in content_disposition:
                    try:
                        body += part.get_payload(decode=True).decode('utf-8', errors='ignore')
                    except:
                        pass
                elif content_type == "text/html" and "attachment" not in content_disposition and not body:
                    # Usa HTML se não tiver texto plano
                    try:
                        html_body = part.get_payload(decode=True).decode('utf-8', errors='ignore')
                        # Remove tags HTML básicas
                        body += re.sub(r'<[^>]+>', '', html_body)
                    except:
                        pass
        else:
            # E-mail não multipart
            try:
                body = msg.get_payload(decode=True).decode('utf-8', errors='ignore')
            except:
                pass
        
        return body
    
    def mark_as_read(self, email_id):
        """Marca e-mail como lido"""
        try:
            self.imap.store(email_id, '+FLAGS', '\\Seen')
        except:
            pass


def load_email_credentials(file_path='account.txt'):
    """
    Carrega credenciais de e-mail do arquivo account.txt
    
    :param file_path: Caminho do arquivo
    :return: Tupla (email, email_password) ou (None, None)
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            credentials = {}
            for line in file:
                line = line.strip()
                if '=' in line:
                    key, value = line.split('=', 1)
                    credentials[key.strip()] = value.strip()
            
            email_addr = credentials.get('email', '')
            email_pass = credentials.get('email_password', '')
            
            if email_addr and email_pass:
                return email_addr, email_pass
            else:
                return None, None
                
    except FileNotFoundError:
        return None, None
    except Exception as e:
        print(f"Erro ao ler credenciais de e-mail: {str(e)}")
        return None, None


# Teste do módulo
if __name__ == "__main__":
    print("=" * 60)
    print("🧪 TESTE DO MÓDULO DE E-MAIL")
    print("=" * 60)
    print()
    
    # Carrega credenciais
    email_addr, email_pass = load_email_credentials()
    
    if not email_addr or not email_pass:
        print("⚠️  Credenciais de e-mail não configuradas em account.txt")
        print("\nAdicione as linhas:")
        print("   email = seu_email@gmail.com")
        print("   email_password = sua_senha_ou_app_password")
        exit(1)
    
    print(f"E-mail configurado: {email_addr}")
    print()
    
    # Cria handler
    handler = EmailHandler(email_addr, email_pass, provider='gmail')
    
    # Conecta
    if handler.connect():
        print("\n✓ Conexão estabelecida com sucesso!")
        print("\n💡 Para testar extração de código:")
        print("   1. Faça login no Mercado Livre manualmente")
        print("   2. Solicite código de verificação por e-mail")
        print("   3. O código será buscado automaticamente")
        
        # Teste de busca (descomente para testar com código real)
        # code = handler.get_verification_code_from_mercadolivre(max_attempts=3)
        # if code:
        #     print(f"\n✓ Código encontrado: {code}")
        
        handler.disconnect()
    else:
        print("\n✗ Falha ao conectar ao e-mail")
        print("\n💡 Verifique:")
        print("   - Credenciais corretas")
        print("   - Acesso IMAP habilitado")
        print("   - Senha de app configurada (Gmail)")
