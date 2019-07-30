
import logging

# create logger
log_level = logging.DEBUG  # logging.DEBUG
logging.basicConfig(level=log_level)
logger = logging.getLogger('postproc.py')
logger.setLevel(level=log_level)


def source_result_postproc(replacer_cpp, node, eq_terms_names=["=", "=-"]):
    
    '''Replace source[delay] or source in eq.lhs to result.
    Ex: source[delay][idx+0]|->result[idx+0]'''
    
    if replacer_cpp.get_node_type(node) in eq_terms_names:
        
        successors = replacer_cpp.get_successors(node)

        left_node = successors[1]
        
        left_node_out = replacer_cpp.get_output_out(left_node)
        
        if left_node_out is None:
            logger.debug("source_result_postproc eq has no cpp output")
            return
        if 'source[delay]' in left_node_out:
            new_out = (left_node_out
                       .replace('source[delay]', 'result'))
        elif 'source' in left_node_out:
            new_out = (left_node_out
                       .replace('source', 'result'))
        else:
            logger.debug("source_result_postproc eq has nothing for"
                         + " source-result conversion")
            return
        replacer_cpp.set_output_out(left_node, new_out)


def delay_postproc(replacers, nodes_lists):

    '''Convert delays for all term's that have it.
    node have or have not global_data['delay_data'] value.
    If have, it will be transformed into cpp corect
    order (for ex: [5.1, 1.5, 2.7]->[3, 1, 2])

    First it collect delays (and remember from whom)
    then convert them,
    finely replace them into it's term.cpp.out string.

    var (like U(t-1.1)) used for factorize delays. In
    that case used only var[0] (U).
    
    Inputs:
    
    - ``replacers`` -- replacer for each equation.

    - ``nodes_lists`` -- list of nodes for each equation.
    count of that list must be equal count of equations
    (and => count of replacers)

    Examples:
    for node:
       term.cpp.global_data['delay_data'] = (1, 'V(t-1.1)', '1.1')
       term.cpp.out = source[delay]
    return:
       term.cpp.out_new = source[coverted delay for 1.1]

    Return:
    (in sent U*U(t-3.1)*V(t-3.3)*U(t-1.3)*V(t-1.1) ...)

    {'converted_delay': 2, 'delay_data': (1, 'U(t-3.1)', '3.1')}
    for U(t-3.1) where:
    converted_delay : source[converted_delay][0]
    delay_data[0] - number of delay's term U(t-3.1)
                    in all delays terms.

    {'converted_delay': 2, 'delay_data': (2, 'V(t-3.3)', '3.3')}
    for V(t-3.3) where:
    converted_delay : source[converted_delay][1]
    delay_data[0] - number of delay's term V(t-3.3)
                    in all delays terms.

    {'converted_delay': 1, 'delay_data': (3, 'U(t-1.3)', '1.3')}
    for U(t-1.3) where:
    converted_delay : source[converted_delay][0]
    delay_data[0] - number of delay's term U(t-1.3)
                    in all delays terms.

    Update:
    It now use term instead of term_id for term identification
    in res[var][delay] = [term] and in map_td.
    '''

    def convert_delays(delays):

        '''Convert float delay to int,
        according it's value.

        For ex:
        [5.1, 1.5, 2.7]->[3, 1, 2]
        '''
        # delays = copy(delays)
        delays.sort()
        sdelays = [delays.index(val)+1 for val in delays]
        logger.debug(sdelays)
        return(zip(delays, sdelays))

    logger.debug("FROM postproc")

    # FOR factorize terms delays for var:
    # res[val] = [(delay_0, term_id_0), ...]
    res = {}
    for i, nodes_list in enumerate(nodes_lists):
        for j, term in enumerate(nodes_list):
            '''
            if type(term) == str:
                continue
            '''
            try:
                term_data = replacers[i].get_output_data(term)
                if term_data is None:
                    continue

                delay_data = term_data["delay_data"]
                # delay_data = term.output.cpp.global_data['delay_data']
                term_id, var, delay = delay_data
                # U(t-1.1)->U
                var = var[0]
                replacer_node_id = (i, j)
                if var in res.keys():
                    if delay in res[var].keys():
                        res[var][delay].append(replacer_node_id)  # term_id
                    else:
                        res[var][delay] = [replacer_node_id]  # term_id
                else:
                    res[var] = {delay: [replacer_node_id]}  # term_id
            except KeyError:
                pass
            except AttributeError:
                # if term not have out:
                # (like +):
                continue
    logger.debug("res")
    logger.debug(res)
    # END FOR

    # FOR map float delays to it's source equivalent:
    # map_dsd: var -> delay, sdelay
    map_dsd = lambda var: convert_delays(list(res[var].keys()))

    # map_td: term_id -> source delay
    map_td = dict([(equal_term, sdelay) for var in res.keys()
                   for delay, sdelay in map_dsd(var)
                   for equal_term in res[var][delay]])
    logger.debug("map_td")
    logger.debug(map_td)
    # END FOR

    # FOR find terms for converted delay:
    out_new = []
    for i, nodes_list in enumerate(nodes_lists):
        for j, term in enumerate(nodes_list):
            try:
                '''
                if type(term) == str:
                    out_new.append(term)
                    continue
                '''
                term_data = replacers[i].get_output_data(term)
                if term_data is None:
                    continue

                delay_data = term_data["delay_data"]
                # delay_data = term.output.cpp.global_data['delay_data']

                # if delay
                # transform source[delay]->source[1]:
                term_id, var, delay = delay_data
                sdelay = map_td[(i, j)]
                # sdelay = map_td[term]  # term_id
                term_out = replacers[i].get_output_out(term)
                if term_out is None:
                    continue
                if 'delay' not in term_out:
                    continue
                replacers[i].set_output_out(term,
                                            term_out.replace('delay',
                                                             str(sdelay)))
                replacers[i].set_output_data(term, 'converted_delay', sdelay)
                '''
                term.output.cpp.out = (term.output
                                       .cpp.out.replace('delay', str(sdelay)))
                term.output.cpp.global_data['converted_delay'] = sdelay
                '''
                out_new.append(term)
            except KeyError:
                # in sdelay = map_td[term]
                try:
                    # if no delay
                    # transform source[delay]->source[0]
                    term_out = replacers[i].get_output_out(term)
                    if term_out is None:
                        continue
                    if 'delay' not in term_out:
                        continue
                    replacers[i].set_output_out(term, term_out.replace('delay',
                                                                       str(0)))
                    '''
                    term.output.cpp.out = (term.output.
                                           cpp.out.replace('delay', str(0)))
                    '''
                    out_new.append(term)
                except:
                    pass
            except AttributeError:
                # if term not have out:
                # (like +):
                out_new.append(term)
    # logger.debug([o.out for o in out_new if type(o) != str])
    # return(out)  # out_new

