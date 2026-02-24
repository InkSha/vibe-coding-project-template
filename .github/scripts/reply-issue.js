import { generateText } from 'ai'
import { createGateway } from 'ai'
import { Octokit } from '@octokit/rest'

function getGateway() {
  if (!process.env.AI_GATEWAY_URL) {
    throw new Error('AI_GATEWAY_URL is required')
  }

  if (!process.env.AI_API_KEY) {
    throw new Error('AI_API_KEY is required')
  }

  return createGateway({
    baseURL: process.env.AI_GATEWAY_URL,
    apiKey: process.env.AI_API_KEY
  })
}

function getOctokit() {
  if (!process.env.GITHUB_TOKEN) {
    throw new Error('GITHUB_TOKEN is required')
  }

  return new Octokit({
    auth: process.env.GITHUB_TOKEN
  })
}

async function main() {
  const gateway = getGateway()
  const octokit = getOctokit()

  const { ISSUE_NUMBER, ISSUE_TITLE, ISSUE_BODY, REPO_OWNER, REPO_NAME, AI_MODEL } = process.env

  console.log(`Processing issue #${ISSUE_NUMBER}: ${ISSUE_TITLE}`)

  if (!AI_MODEL) {
    throw new Error('AI_MODEL is required')
  }

  const { text } = await generateText({
    model: gateway(AI_MODEL),
    system: `You are a code assistant that helps users solve problems in GitHub Issues.
            Analyze the problem and provide a solution or code modification suggestion.`,
    prompt: `Issue title: ${ISSUE_TITLE}\n\nIssue content:\n${ISSUE_BODY}`
  })

  await octokit.issues.createComment({
    owner: REPO_OWNER || '',
    repo: REPO_NAME || '',
    issue_number: parseInt(ISSUE_NUMBER || ''),
    body: `🤖 ${AI_MODEL} reply:\n\n${text}`
  })

  console.log('Done')
}

main().catch(console.error)
