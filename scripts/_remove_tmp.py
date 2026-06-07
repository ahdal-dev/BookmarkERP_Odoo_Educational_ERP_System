module = env['ir.module.module'].search([('name', '=', 'admission_portal'), ('state', '=', 'installed')]) 
if module: 
    module.button_immediate_uninstall() 
    print('Module admission_portal uninstalled successfully.') 
else: 
    print('Module admission_portal is not installed or not found.') 
