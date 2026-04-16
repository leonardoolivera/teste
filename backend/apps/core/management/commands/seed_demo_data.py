from datetime import timedelta

from django.core.management.base import BaseCommand
from django.db import transaction
from django.utils import timezone

from apps.catalog.models import Author, BibliographicRecord, ItemCopy, Subject
from apps.circulation.models import Loan, Reservation, ReturnReceipt
from apps.circulation.services import process_overdue_loans
from apps.core.models import Campus, Institution, LibraryBranch
from apps.inventory.models import InventoryCampaign, InventoryScanSession
from apps.inventory.services import register_scan
from apps.notifications.services import notify_loan_created, notify_return_receipt_created
from apps.users.models import Patron, User


class Command(BaseCommand):
    help = 'Seeds demo data for the IFMS Biblioteca Plataforma.'

    @transaction.atomic
    def handle(self, *args, **options):
        now = timezone.now()

        institution, _ = Institution.objects.update_or_create(
            code='IFMS',
            defaults={
                'name': 'Instituto Federal de Mato Grosso do Sul',
                'email': 'bibliotecas@ifms.local',
                'is_active': True,
            },
        )
        campus, _ = Campus.objects.update_or_create(
            institution=institution,
            code='CG',
            defaults={
                'name': 'Campus Campo Grande',
                'city': 'Campo Grande',
                'state': 'MS',
            },
        )
        branch, _ = LibraryBranch.objects.update_or_create(
            campus=campus,
            code='BIB-CENTRAL',
            defaults={
                'name': 'Biblioteca Central',
                'email': 'biblioteca.cg@ifms.local',
                'phone': '(67) 99999-0000',
                'is_active': True,
            },
        )

        admin_user = self.ensure_user(
            email='admin@ifms.local',
            password='Biblioteca!2026',
            role=User.Role.ADMIN,
            first_name='Ada',
            last_name='Biblioteca',
            branch=branch,
            is_staff=True,
            is_superuser=True,
        )
        librarian_user = self.ensure_user(
            email='bibliotecario@ifms.local',
            password='Biblioteca!2026',
            role=User.Role.LIBRARIAN,
            first_name='Caio',
            last_name='Ramos',
            branch=branch,
            is_staff=True,
            is_superuser=False,
        )

        patrons = {
            'ana': self.ensure_patron(
                registration_code='DEMO-STU-001',
                full_name='Ana Clara Souza',
                email='ana.clara@ifms.local',
                category=Patron.Category.STUDENT,
                branch=branch,
            ),
            'bruno': self.ensure_patron(
                registration_code='DEMO-STU-002',
                full_name='Bruno Henrique Lima',
                email='bruno.henrique@ifms.local',
                category=Patron.Category.STUDENT,
                branch=branch,
            ),
            'camila': self.ensure_patron(
                registration_code='DEMO-TEA-001',
                full_name='Camila Ribeiro',
                email='camila.ribeiro@ifms.local',
                category=Patron.Category.TEACHER,
                branch=branch,
            ),
        }

        machado = Author.objects.get_or_create(name='Machado de Assis')[0]
        turing = Author.objects.get_or_create(name='Alan Turing')[0]
        clarice = Author.objects.get_or_create(name='Clarice Lispector')[0]
        dados = Subject.objects.get_or_create(name='Ciencia de Dados')[0]
        literatura = Subject.objects.get_or_create(name='Literatura Brasileira')[0]
        algoritmos = Subject.objects.get_or_create(name='Algoritmos')[0]

        record_dom_casmurro = self.ensure_record(
            isbn='9788503012300',
            title='Dom Casmurro',
            subtitle='Edicao comentada para ensino medio e superior',
            publication_year=2022,
            publisher='Editora Machado',
            classification_code='869.93',
            authors=[machado],
            subjects=[literatura],
        )
        record_dados = self.ensure_record(
            isbn='9786500101010',
            title='Fundamentos de Ciencia de Dados',
            subtitle='Do catalogo ao painel gerencial',
            publication_year=2024,
            publisher='Editora IFMS Tech',
            classification_code='006.3',
            authors=[turing],
            subjects=[dados, algoritmos],
        )
        record_estrela = self.ensure_record(
            isbn='9788520923214',
            title='A Hora da Estrela',
            subtitle='Leitura orientada para clubes e mediacao',
            publication_year=2023,
            publisher='Editora Clarice',
            classification_code='869.94',
            authors=[clarice],
            subjects=[literatura],
        )
        record_redes = self.ensure_record(
            isbn='9786500102024',
            title='Redes e Infraestrutura para Bibliotecas Inteligentes',
            subtitle='Operacao segura, RFID e automacao',
            publication_year=2025,
            publisher='Infra Campus Press',
            classification_code='004.6',
            authors=[turing],
            subjects=[dados, algoritmos],
        )

        copy_dom_1 = self.ensure_copy(
            asset_code='PAT-0001',
            record=record_dom_casmurro,
            branch=branch,
            barcode='BAR-0001',
            rfid_tag='RFID-0001',
            shelf_location='A1-01',
            tomb_number='TOMBO-0001',
        )
        copy_dom_2 = self.ensure_copy(
            asset_code='PAT-0002',
            record=record_dom_casmurro,
            branch=branch,
            barcode='BAR-0002',
            rfid_tag='RFID-0002',
            shelf_location='A1-02',
            tomb_number='TOMBO-0002',
        )
        copy_dados_1 = self.ensure_copy(
            asset_code='PAT-0003',
            record=record_dados,
            branch=branch,
            barcode='BAR-0003',
            rfid_tag='RFID-0003',
            shelf_location='B2-01',
            tomb_number='TOMBO-0003',
        )
        copy_dados_2 = self.ensure_copy(
            asset_code='PAT-0004',
            record=record_dados,
            branch=branch,
            barcode='BAR-0004',
            rfid_tag='RFID-0004',
            shelf_location='B2-02',
            tomb_number='TOMBO-0004',
        )
        copy_estrela = self.ensure_copy(
            asset_code='PAT-0005',
            record=record_estrela,
            branch=branch,
            barcode='BAR-0005',
            rfid_tag='RFID-0005',
            shelf_location='C3-01',
            tomb_number='TOMBO-0005',
        )
        copy_redes = self.ensure_copy(
            asset_code='PAT-0006',
            record=record_redes,
            branch=branch,
            barcode='BAR-0006',
            rfid_tag='RFID-0006',
            shelf_location='D4-01',
            tomb_number='TOMBO-0006',
        )

        open_loan, open_created = Loan.objects.get_or_create(
            patron=patrons['ana'],
            item_copy=copy_dados_1,
            returned_at__isnull=True,
            defaults={
                'checked_out_by': librarian_user,
                'due_at': now + timedelta(days=6),
                'status': Loan.Status.OPEN,
            },
        )
        if not open_created:
            open_loan.checked_out_by = librarian_user
            open_loan.due_at = now + timedelta(days=6)
            open_loan.status = Loan.Status.OPEN
            open_loan.returned_at = None
            open_loan.fine_amount = '0.00'
            open_loan.save(update_fields=['checked_out_by', 'due_at', 'status', 'returned_at', 'fine_amount', 'updated_at'])
        copy_dados_1.status = ItemCopy.Status.LOANED
        copy_dados_1.save(update_fields=['status', 'updated_at'])
        if open_created:
            notify_loan_created(open_loan)

        overdue_loan, _ = Loan.objects.get_or_create(
            patron=patrons['bruno'],
            item_copy=copy_dom_1,
            returned_at__isnull=True,
            defaults={
                'checked_out_by': librarian_user,
                'due_at': now - timedelta(days=8),
                'status': Loan.Status.OPEN,
            },
        )
        overdue_loan.checked_out_by = librarian_user
        overdue_loan.due_at = now - timedelta(days=8)
        overdue_loan.status = Loan.Status.OPEN
        overdue_loan.returned_at = None
        overdue_loan.fine_amount = '0.00'
        overdue_loan.save(update_fields=['checked_out_by', 'due_at', 'status', 'returned_at', 'fine_amount', 'updated_at'])
        copy_dom_1.status = ItemCopy.Status.LOANED
        copy_dom_1.save(update_fields=['status', 'updated_at'])

        returned_loan = Loan.objects.filter(patron=patrons['camila'], item_copy=copy_estrela).first()
        if returned_loan is None:
            returned_loan = Loan.objects.create(
                patron=patrons['camila'],
                item_copy=copy_estrela,
                checked_out_by=librarian_user,
                due_at=now - timedelta(days=2),
                returned_at=now - timedelta(days=1),
                status=Loan.Status.RETURNED,
                fine_amount='0.00',
            )
        else:
            returned_loan.checked_out_by = librarian_user
            returned_loan.due_at = now - timedelta(days=2)
            returned_loan.returned_at = now - timedelta(days=1)
            returned_loan.status = Loan.Status.RETURNED
            returned_loan.fine_amount = '0.00'
            returned_loan.save(update_fields=['checked_out_by', 'due_at', 'returned_at', 'status', 'fine_amount', 'updated_at'])
        copy_estrela.status = ItemCopy.Status.AVAILABLE
        copy_estrela.save(update_fields=['status', 'updated_at'])

        receipt, receipt_created = ReturnReceipt.objects.get_or_create(
            loan=returned_loan,
            defaults={
                'returned_by': librarian_user,
                'return_token': 'IFMS-DEV-RETORNO-0001',
                'notes': 'Devolucao de demonstracao criada automaticamente.',
            },
        )
        if not receipt_created and receipt.return_token != 'IFMS-DEV-RETORNO-0001':
            receipt.return_token = 'IFMS-DEV-RETORNO-0001'
            receipt.returned_by = librarian_user
            receipt.notes = 'Devolucao de demonstracao criada automaticamente.'
            receipt.save(update_fields=['return_token', 'returned_by', 'notes', 'updated_at'])
        if receipt_created:
            notify_return_receipt_created(receipt)

        reservation, _ = Reservation.objects.get_or_create(
            patron=patrons['camila'],
            bibliographic_record=record_dom_casmurro,
            defaults={
                'pickup_branch': branch,
                'status': Reservation.Status.QUEUED,
                'queue_position': 1,
            },
        )
        reservation.pickup_branch = branch
        reservation.status = Reservation.Status.QUEUED
        reservation.queue_position = 1
        reservation.fulfilled_item_copy = None
        reservation.expires_at = None
        reservation.save(update_fields=['pickup_branch', 'status', 'queue_position', 'fulfilled_item_copy', 'expires_at', 'updated_at'])

        process_overdue_loans(now=now)

        campaign, _ = InventoryCampaign.objects.update_or_create(
            library_branch=branch,
            name='Inventario anual 2026 - Biblioteca Central',
            defaults={
                'status': InventoryCampaign.Status.ACTIVE,
                'opened_by': librarian_user,
                'started_at': now - timedelta(hours=4),
                'notes': 'Campanha de demonstracao para o scanner patrimonial.',
            },
        )
        campaign.reads.all().delete()
        campaign.scan_sessions.all().delete()
        session = InventoryScanSession.objects.create(
            campaign=campaign,
            operator=librarian_user,
            device_label='coletor-demo-01',
            source_hint='rfid-camera-hibrido',
            notes='Sessao demo carregada pelo comando seed_demo_data.',
        )
        register_scan(campaign=campaign, session=session, operator=librarian_user, scanned_code='PAT-0002', scan_source='patrimony', device_label='coletor-demo-01')
        register_scan(campaign=campaign, session=session, operator=librarian_user, scanned_code='BAR-0004', scan_source='barcode', device_label='coletor-demo-01')
        register_scan(campaign=campaign, session=session, operator=librarian_user, scanned_code='RFID-0006', scan_source='rfid', device_label='coletor-demo-01')
        register_scan(campaign=campaign, session=session, operator=librarian_user, scanned_code='PATRIMONIO-INEXISTENTE', scan_source='manual', device_label='coletor-demo-01')

        self.stdout.write(self.style.SUCCESS('Demo data seeded successfully.'))
        self.stdout.write('Backoffice credentials: admin@ifms.local / Biblioteca!2026')
        self.stdout.write('Support credentials: bibliotecario@ifms.local / Biblioteca!2026')
        self.stdout.write('Public return token: IFMS-DEV-RETORNO-0001')

    def ensure_user(self, *, email, password, role, first_name, last_name, branch, is_staff, is_superuser):
        user, _ = User.objects.get_or_create(
            email=email,
            defaults={
                'username': email,
                'first_name': first_name,
                'last_name': last_name,
                'role': role,
                'library_branch': branch,
                'is_staff': is_staff,
                'is_superuser': is_superuser,
                'is_active': True,
            },
        )
        user.first_name = first_name
        user.last_name = last_name
        user.role = role
        user.library_branch = branch
        user.is_staff = is_staff
        user.is_superuser = is_superuser
        user.is_active = True
        user.set_password(password)
        user.save()
        return user

    def ensure_patron(self, *, registration_code, full_name, email, category, branch):
        patron, _ = Patron.objects.get_or_create(
            registration_code=registration_code,
            defaults={
                'full_name': full_name,
                'email': email,
                'category': category,
                'status': Patron.Status.ACTIVE,
                'library_branch': branch,
            },
        )
        patron.full_name = full_name
        patron.email = email
        patron.category = category
        patron.status = Patron.Status.ACTIVE
        patron.library_branch = branch
        patron.save(update_fields=['full_name', 'email', 'category', 'status', 'library_branch', 'updated_at'])
        return patron

    def ensure_record(self, *, isbn, title, subtitle, publication_year, publisher, classification_code, authors, subjects):
        record, _ = BibliographicRecord.objects.get_or_create(
            isbn=isbn,
            defaults={
                'title': title,
                'subtitle': subtitle,
                'publication_year': publication_year,
                'publisher': publisher,
                'language': 'pt-BR',
                'edition_statement': '1a edicao',
                'classification_code': classification_code,
                'cutter': title[:3].upper(),
                'description': f'Registro de demonstracao para {title}.',
            },
        )
        record.title = title
        record.subtitle = subtitle
        record.publication_year = publication_year
        record.publisher = publisher
        record.language = 'pt-BR'
        record.edition_statement = '1a edicao'
        record.classification_code = classification_code
        record.cutter = title[:3].upper()
        record.description = f'Registro de demonstracao para {title}.'
        record.save()
        record.authors.set(authors)
        record.subjects.set(subjects)
        return record

    def ensure_copy(self, *, asset_code, record, branch, barcode, rfid_tag, shelf_location, tomb_number):
        copy, _ = ItemCopy.objects.get_or_create(
            asset_code=asset_code,
            defaults={
                'bibliographic_record': record,
                'library_branch': branch,
                'barcode': barcode,
                'rfid_tag': rfid_tag,
                'shelf_location': shelf_location,
                'tomb_number': tomb_number,
                'status': ItemCopy.Status.AVAILABLE,
                'notes': 'Exemplar de demonstracao.',
            },
        )
        copy.bibliographic_record = record
        copy.library_branch = branch
        copy.barcode = barcode
        copy.rfid_tag = rfid_tag
        copy.shelf_location = shelf_location
        copy.tomb_number = tomb_number
        copy.notes = 'Exemplar de demonstracao.'
        if copy.status not in {ItemCopy.Status.LOANED, ItemCopy.Status.AVAILABLE}:
            copy.status = ItemCopy.Status.AVAILABLE
        copy.save()
        return copy