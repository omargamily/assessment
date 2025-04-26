from celery import shared_task
from .services import update_installment_statuses, check_upcoming_installments
from celery.utils.log import get_task_logger

logger = get_task_logger(__name__)

@shared_task
def update_installment_statuses_task():
    """
    Celery task to update installment statuses.
    Updates installments to 'Due' or 'Late' based on their due dates.
    """
    try:
        updated_count = update_installment_statuses()
        logger.info(f'Successfully updated {updated_count} installment(s)')
        return updated_count
    except Exception as e:
        logger.error(f'Error updating installment statuses: {str(e)}')
        raise

@shared_task
def check_upcoming_installments_task():
    """
    Celery task to check for installments due in 3 days and log notifications.
    """
    try:
        upcoming = check_upcoming_installments()
        for installment in upcoming:
            logger.info(
                f"UPCOMING INSTALLMENT NOTIFICATION: "
                f"User {installment.plan.user.email} has an installment of "
                f"${installment.amount} due in 3 days (Due date: {installment.due_date})"
            )
        return len(upcoming)
    except Exception as e:
        logger.error(f'Error checking upcoming installments: {str(e)}')
        raise