"""Local-only descriptive dispatch inventory; never loads or runs validators."""
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
# These entry profiles follow p1_adapter._validator_for; higher versions depend
# on the preceding modules. Presence is deliberately not an import/health check.
PROFILES = (
    ('P1-VC/1.0.0', 'semantic-validator-v1/cube_semantic/validator.py'),
    ('P1.6/instantiation-profile-v1', 'instantiation-profile-v1/cube_p16/validator.py'),
    ('P1.8/simulation-profile-v1', 'simulation-profile-v1/cube_p18/validator.py'),
    ('P1.9/comparison-profile-v1', 'comparison-profile-v1/cube_p19/validator.py'),
    ('P1.10/migration-profile-v1', 'migration-profile-v1/cube_p110/validator.py'),
    ('P1.10.1/migration-profile-v2', 'migration-profile-v2/cube_p1101/validator.py'),
    ('P1.11/migration-methods-v1', 'migration-methods-v1/cube_p111/validator.py'),
    ('P1.12/coverage-instance-profile-v1', 'coverage-instance-profile-v1/cube_p112/validator.py'),
    ('P1.13/control-flow-profile-v1', 'control-flow-profile-v1/cube_p113/validator.py'),
    ('P1.14/relation-origin-profile-v1', 'relation-origin-profile-v1/cube_p114/validator.py'),
    ('P1.15/scope-nesting-profile-v1', 'scope-nesting-profile-v1/cube_p115/validator.py'),
)

def describe_validation_contexts():
    contexts = []
    for index, (profile, _) in enumerate(PROFILES, 1):
        sources = ['P1/' + source for _, source in PROFILES[:index]]
        contexts.append({
            'context_format': 'aiaeao.cube.binding-context/' + str(index),
            'entry_profile': profile,
            'dispatch_implemented': True,
            'required_sources': sources,
            'required_sources_present': all((ROOT / p).is_file() for p in sources),
            'runtime_load_verified': False,
            **({'diagnostic_codes': ['P1_ORIGIN_UNDECLARED', 'P1_ORIGIN_BASIS_MISSING',
                                      'P1_ORIGIN_INVALID']} if index == 10 else {}),
            **({'diagnostic_codes': ['P1_SCOPE_NESTING_INVALID', 'P1_ADMISSION_OUTCOME_CONFLICT']} if index == 11 else {}),
        })
    return {
        'format': 'aiaeao.cube.local-validation-discovery/1',
        'selection': 'explicit_context_format_no_auto_upgrade',
        'context_omitted': 'base_P1_validation_without_declared_binding_context',
        'contexts': contexts,
        'presence_is_not_runtime_validation': True,
        'evaluation_performed_by_cube': False,
        'method_execution_by_cube': False,
        'truth_authority_admission': 'NOT_EVALUATED',
    }
