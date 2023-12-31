from django.forms import model_to_dict

from common.models import Components, ComponentsStatus


def component_group_order(query):
    local_final_dict = dict()
    local_final_dict['component_id'] = query.component_id
    local_final_dict['component_name'] = query.component_name
    local_final_dict['group_no'] = query.group_no
    local_final_dict['has_subgroup'] = query.has_subgroup
    local_final_dict['businessunit'] = model_to_dict(query.businessunit)
    local_final_dict['component_status'] = model_to_dict(
        query.component_status)
    return local_final_dict


def get_component_status(Status_name=None):
    comp_status_obj = ComponentsStatus.objects.values(
        'component_status_id', 'component_status_name')
    status_id = None
    for obj_data in comp_status_obj:
        if obj_data['component_status_name'] == Status_name:
            status_id = obj_data['component_status_id']
            break
    return status_id


def get_components_all_list(queryset,):

    finaldata_list = list()
    groups_qa = queryset.filter(is_group=True)
    subgroup_qs = queryset.filter(is_group=False)
    for query in groups_qa:
        local_list = list()
        local_final_dict = component_group_order(query)
        for subgp_data in subgroup_qs:
            local_temp_dict = dict()
            if query.group_no == subgp_data.group_no:
                local_temp_dict = component_group_order(subgp_data)
                local_list.append(local_temp_dict)
        local_final_dict['sub_component'] = local_list
        finaldata_list.append(local_final_dict)
    return finaldata_list
