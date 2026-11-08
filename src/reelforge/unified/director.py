"""Trusted data adapter preserving the original Director V3 storyboard grammar."""
from reelforge.mvp.planner import Beat
from reelforge.mvp.storylib import build_directed_shot
from reelforge.mvp.dressing import dress_storyboard, DRESSING
from reelforge.productions.contract import compile_production
from .contract import fail, _assets


def compile_events(request, spans):
    segments, coverage, signatures, warnings = [], [], [], []
    for e, (start, end) in zip(request['events'], spans):
        if not {'world', 'mood', 'shots'} <= e.keys():
            fail('/events/' + e['id'], 'Director event needs world, mood and explicit shot recipes')
        if len(e['shots']) * 90 != end - start:
            fail('/events/' + e['id'], 'Shot count must exactly fill approved event interval')
        event_assets, shots = set(), []
        forbidden = [key for key, spec in DRESSING.items() if spec.asset in e['forbidden_assets']]
        beacon = 'beacon_01' in e['required_assets'] or 'answer_light_01' in e['required_assets']
        for raw in e['shots']:
            preset, style, world = raw['preset'], raw['style'], e['world']
            if preset in ('investigate','threat') and (world != 'frost_peak' or not beacon):
                fail('/events/' + e['id'], 'Beacon set pieces require ridge and explicit beacon asset')
            if (raw['weather'] and world != 'frost_peak') or (style.startswith('run_') and preset != 'travel_run'):
                fail('/events/' + e['id'], 'Weather/run style incompatible with selected world/preset')
            if style == 'parcel_reveal' and (world != 'orchard' or preset != 'reaction'):
                fail('/events/' + e['id'], 'Parcel reveal requires orchard reaction')
            index = len(segments)
            title = f"{request['id']} shot {index+1}"
            beat = Beat(preset, world, e['mood'], title, e['label'], raw['variant'], style, raw['weather'])
            board = build_directed_shot(preset, world, title=title, description=e['label'], mood=e['mood'],
                                       variant=raw['variant'], style=style, weather=raw['weather'], beacon=beacon)
            dress_storyboard(board, beat, forbidden=forbidden)
            active = {n['asset_id'] for n in board['world']['nodes'] if n.get('visible') and n.get('asset_id')}
            if set(e['forbidden_assets']) & active:
                fail('/events/' + e['id'], 'Forbidden asset remains staged in recipe')
            event_assets |= active
            actions = [b['action']['kind'] for b in board['beats']]
            row = {'shot': index+1,'start_frame': index*90,'end_frame':(index+1)*90,
                   'preset':preset, 'style':style, 'world':world, 'actions':actions,
                   'camera': board['views'][0]['kind'], 'assets': sorted(active),
                   'character':'yellow_mellow_v2','variant':'reference_slim'}
            signatures.append((world,preset,style,raw['variant']))
            shots.append(row)
            segments.append({'id': f'seg_{index+1:02d}', 'storyboard':board})
        _assets(e, event_assets)
        coverage.append({'id':e['id'],'label':e['label'],'start_frame':start,'end_frame':end,
                         'assets':sorted(event_assets),'shots':shots})
    if len(set(signatures)) < .8 * len(signatures):
        warnings.append('More than one fifth of shot recipes repeat; inspect composition and story rhythm')
    warnings.append('Director gait clocks reset at shot cuts; ridge travel is level, not downhill')
    manifest = {'schema_version':'production-0.1','title':request['title'],'segments':segments,'audio':None}
    return compile_production(manifest), manifest, coverage, warnings
