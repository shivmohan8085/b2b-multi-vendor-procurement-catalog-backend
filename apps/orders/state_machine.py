"""Order status transition rules."""

ALLOWED_TRANSITIONS = {
    'draft': ['pending_approval', 'cancelled'],
    'pending_approval': ['approved', 'rejected', 'cancelled'],
    'approved': ['sent_to_vendor', 'cancelled'],
    'rejected': [],
    'sent_to_vendor': ['accepted_by_vendor', 'cancelled'],
    'accepted_by_vendor': ['partially_delivered', 'delivered', 'cancelled'],
    'partially_delivered': ['delivered'],
    'delivered': ['invoiced'],
    'invoiced': ['completed'],
    'completed': [],
    'cancelled': [],
}


def can_transition(from_status, to_status):
    return to_status in ALLOWED_TRANSITIONS.get(from_status, [])