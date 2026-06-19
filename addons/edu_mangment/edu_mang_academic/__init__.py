from . import models


def post_init_hook(env):
    """Seed sample grades on existing enrolled registrations so cumulative GPA,
    earned credits, and academic standing are demonstrable right after install."""
    sample = ['A', 'B+', 'A-', 'B', 'C+', 'A', 'B-', 'B+']
    regs = env['education.registration'].search([
        ('state', '=', 'enrolled'),
        ('grade', '=', False),
    ])
    for i, reg in enumerate(regs):
        reg.grade = sample[i % len(sample)]
