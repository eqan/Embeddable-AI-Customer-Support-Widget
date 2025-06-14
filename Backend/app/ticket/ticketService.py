from ticket.models.ticket import Ticket
from ticket.dtos.ticket import TicketCreate, TicketUpdate, DeleteTicket
from config.config import Session

class TicketService:
    def __init__(self):
        self.db = Session()

    def create_ticket(self, ticket: TicketCreate):
        try:
            self.db.add(Ticket(**ticket.model_dump()))
            self.db.commit()
            return ticket
        except Exception as e:
            self.db.rollback()
            raise e
        
    def update_ticket(self, ticket: TicketUpdate):
        try:
            self.db.query(Ticket).filter(Ticket.uuid == ticket.uuid).update(ticket.model_dump())
            self.db.commit()
            return ticket
        except Exception as e:
            self.db.rollback()
            raise e
        
    def delete_ticket(self, ticket: DeleteTicket):
        try:
            self.db.query(Ticket).filter(Ticket.uuid == ticket.uuid).delete()
            self.db.commit()
            return ticket
        except Exception as e:
            self.db.rollback()
            raise e
        
    def get_ticket(self, uuid: str):
        try:
            return self.db.query(Ticket).filter(Ticket.uuid == uuid).first()
        except Exception as e:
            raise e
    
    def get_all_tickets_by_user_id(self, user_id: int):
        try:
            return self.db.query(Ticket).filter(Ticket.user_id == user_id).all()
        except Exception as e:
            raise e