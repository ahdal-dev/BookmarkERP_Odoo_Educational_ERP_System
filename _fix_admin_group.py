env = self.env
admin_user = env['res.users'].browse(2)
group = env.ref('edu_mang_auth.group_erp_admin')
admin_user.write({'group_ids': [(4, group.id)]})
env.cr.commit()
print(f"OK: added admin uid=2 to group {group.name} id={group.id}")
print(f"Verified: {group.id in admin_user.group_ids.ids}")
