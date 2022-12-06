def component_group_order(query):
    local_final_dict = dict()
    local_final_dict['component_id'] = query.component_id
    local_final_dict['component_name'] = query.component_name
    local_final_dict['businessunit_id'] = query.businessunit.businessunit_id
    local_final_dict['businessunit_name'] = query.businessunit.businessunit_name
    local_final_dict['component_status'] = query.component_status.component_status_name
    local_final_dict['group_no'] = query.group_no
    return local_final_dict
