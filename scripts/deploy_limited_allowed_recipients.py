from brownie import chain, network

from utils.config import (
    get_env,
    get_is_live,
    get_deployer_account,
    prompt_bool,
    network_name
)
from utils import (
    deployment,
    lido,
    deployed_easy_track,
    log
)

from brownie import (
    AllowedRecipientsRegistry,
    AddAllowedRecipient,
    RemoveAllowedRecipient,
    TopUpAllowedRecipients
)

def main():
    netname = "goerli" if network_name().split('-')[0] == "goerli" else "mainnet"

    contracts = lido.contracts(network=netname)
    et_contracts = deployed_easy_track.contracts(network=netname)
    deployer = get_deployer_account(get_is_live(), network=netname)

    easy_track = et_contracts.easy_track
    evm_script_executor = et_contracts.evm_script_executor

    # address allowed to create motions to add, remove or top up allowed recipients
    committee_multisig = get_env("COMMITTEE_MULTISIG")

    bokkyPooBahsDateTimeContract = get_env("BOOKYPOOBAH_DATETIME_CONTRACT")
    log.br()

    log.nb("Current network", network.show_active(), color_hl=log.color_magenta)
    log.nb("Using deployed addresses for", netname, color_hl=log.color_yellow)
    log.ok("chain id", chain.id)
    log.ok("Deployer", deployer)
    log.ok("Governance Token", contracts.ldo)
    log.ok("Aragon Voting", contracts.aragon.voting)
    log.ok("Aragon Finance", contracts.aragon.finance)

    log.br()

    log.nb("Committee Multisig", committee_multisig)
    log.nb("Deployed EasyTrack", easy_track)
    log.nb("Deployed EVMScript Executor", evm_script_executor)

    log.br()

    print("Proceed? [yes/no]: ")

    if not prompt_bool():
        log.nb("Aborting")
        return

    tx_params = { "from": deployer }
    if (get_is_live()):
        tx_params["priority_fee"] = "2 gwei"
        tx_params["max_fee"] = "300 gwei"

    (
        allowed_recipients_registry,
        add_allowed_recipient,
        remove_allowed_recipient,
        top_up_allowed_recipients
    ) = deploy_allowed_recipients_contracts(
        evm_script_executor=evm_script_executor,
        lido_contracts=contracts,
        allowed_recipients_multisig=committee_multisig,
        easy_track=easy_track,
        bokkyPooBahsDateTimeContract=bokkyPooBahsDateTimeContract,
        tx_params=tx_params,
    )

    log.br()

    log.ok("Allowed recipients factories have been deployed...")
    log.nb("Deployed AllowedRecipientsRegistry", allowed_recipients_registry)
    log.nb("Deployed AddAllowedRecipient", add_allowed_recipient)
    log.nb("Deployed RemoveAllowedRecipient", remove_allowed_recipient)
    log.nb("Deployed TopUpAllowedRecipients", top_up_allowed_recipients)

    log.br()

    if (get_is_live() and get_env("FORCE_VERIFY", False)):
        log.ok("Trying to verify contracts...")
        AllowedRecipientsRegistry.publish_source(allowed_recipients_registry)
        AddAllowedRecipient.publish_source(add_allowed_recipient)
        RemoveAllowedRecipient.publish_source(remove_allowed_recipient)
        TopUpAllowedRecipients.publish_source(top_up_allowed_recipients)

    log.br()

    if easy_track.hasRole(easy_track.DEFAULT_ADMIN_ROLE(), contracts.aragon.voting):
        log.ok("Easy Track is under DAO Voting control")
        log.ok("To finalize deploy, please create voting that adds factories to Easy Track")
    else:
        log.ok("Easy Track is under another account's control")
        log.ok("To finalize deploy, please manually add factories to Easy Track")

    print("Hit <Enter> to quit script")
    input()


def deploy_allowed_recipients_contracts(
    evm_script_executor,
    lido_contracts,
    allowed_recipients_multisig,
    easy_track,
    bokkyPooBahsDateTimeContract,
    tx_params,
):
    allowed_recipients_registry = deployment.deploy_allowed_recipients_registry(
        voting=lido_contracts.aragon.voting,
        evm_script_executor=evm_script_executor,
        easy_track=easy_track,
        bokkyPooBahsDateTimeContract=bokkyPooBahsDateTimeContract,
        tx_params=tx_params,
    )
    add_allowed_recipient = deployment.deploy_add_allowed_recipient(
        allowed_recipients_registry=allowed_recipients_registry,
        allowed_recipients_multisig=allowed_recipients_multisig,
        tx_params=tx_params,
    )
    remove_allowed_recipient = deployment.deploy_remove_allowed_recipient(
        allowed_recipients_registry=allowed_recipients_registry,
        allowed_recipients_multisig=allowed_recipients_multisig,
        tx_params=tx_params,
    )
    top_up_allowed_recipients = deployment.deploy_top_up_allowed_recipients(
        finance=lido_contracts.aragon.finance,
        governance_token=lido_contracts.ldo,
        allowed_recipients_registry=allowed_recipients_registry,
        allowed_recipients_multisig=allowed_recipients_multisig,
        tx_params=tx_params,
    )

    return (
        allowed_recipients_registry,
        add_allowed_recipient,
        remove_allowed_recipient,
        top_up_allowed_recipients
    )
