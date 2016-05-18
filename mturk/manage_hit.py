import sys
from boto.mturk.connection import HIT

def get_all_reviewable_hits(page_size=50):
    hits = mtc.get_reviewable_hits(page_size=page_size)
    print "Total results to fetch %s " % hits.TotalNumResults
    print "Request hits page %i" % 1

    total_pages = float(hits.TotalNumResults)/page_size
    int_total= int(total_pages)
    if(total_pages-int_total>0):
        total_pages = int_total+1
    else:
        total_pages = int_total
    pn = 1
    while pn < total_pages:
        pn = pn + 1
        print "Request hits page %i" % pn
        temp_hits = mtc.get_reviewable_hits(page_size=page_size,page_number=pn)
        hits.extend(temp_hits)

    return hits



def show_assignments(hit_id):    
    assignments = mtc.get_assignments(hit_id)
    print assignments
    for assignment in assignments:
        show_assignment(assignment)
        print "---------------"

def show_assignment(assignment):
    print "Assignment:"
    print "id: %s" % assignment.AssignmentId
    print "WorkerId: %s" % assignment.WorkerId
    print "HITId: %s" % assignment.HITId

def show_hit(hit):
    print "hit id: %s" % hit.HITId
    print "has expired: %s" % hit.expired
    print "title: %s" % hit.Title
    print "status: %s" % hit.HITStatus
    
    print "=============================="
    show_assignments(hit_id)

def get_hit(hit_id):
    hit = mtc.get_hit(hit_id)[0]
    return hit

def get_assignment(assignment_id):
    assignment = mtc.get_assignment(assignment_id)

def expire_hit(hit_id):
    expire = mtc.expire_hit(hit_id)
    return expire

def approve_rejected_assignment(assignment_id, feedback=None):
    approve = mtc.approve_rejected_assignment(assignment_id)
    if approve:
        return True
    else:
        return False

if __name__ == "__main__":
    if len(sys.argv) == 1:
        print "python manage_hit.py show_assignment assignment_id"
        print "python manage_hit.py unreject assignment_id"
        print "python manage_hit.py expire_hit hit_id"
        print "python manage_hit.py show_hit hit_id"
        exit(0)
    else:
        function = sys.argv[1]
        if len(sys.argv) == 2:
            print "python manage_hit.py show_assignment assignment_id"
            print "python manage_hit.py unreject assignment_id"
            print "python manage_hit.py expire_hit hit_id"
            print "python manage_hit.py show_hit hit_id"
            exit(0)

        if function == "show_assignment":
            assignment_id = sys.argv[2]
            assignment = get_assignment(assignment_id)
            show_assignment(assignment)
            
        elif function == "expire_hit":
            hit_id = sys.argv[2]
            expire = expire_hit(hit_id)
            print "expire hit: %s" % hit_id
            print expire

        elif function == "unreject":
            assignment_id = sys.argv[2]
            approve_rejected_assignment(assignment_id)
            print "unreject assignment %s" % assignment_id

        elif function == "show_hit":
             hit_id = sys.argv[2]
             hit = get_hit(hit_id)
             show_hit(hit)
