# Templates — The testing skill

### The testing skill proves a change by its risk

The project's testing skill holds the rule that the plan, the fix round and
the review's `test` lens all read, so it is written once:

- **The risk classes.** A change in one ships with its test in the same
  commit, and the test fails without the change: money; data written or
  deleted, and what decides which rows; access; a merge of records or
  accounts; what lets a confirmation through, or blocks it; logic that
  branches on its input; and what breaks where nobody looks — the request a
  page assembles (a field's name, a hidden fingerprint, the form a checkbox
  or a button belongs to, a `formaction`), what lets a key, a tap or a
  submit reach an action (above all one that deletes or charges), a
  contract of shared code other screens lean on (a lock taken and released,
  a queue that moves, a global flag reset, a fallback that never leaves the
  user stuck), a path the local check cannot reach (the exchange with a
  provider, a slow or failing network, a first visit, reduced motion,
  touch). The last class holds on one condition, on any screen: the break
  costs data, access, a merge or a payment, or leaves the user stuck; a
  break of the look alone is outside it. Any other behaviour is checked
  live, and the check is recorded.
- **What a test asserts** — the decision: the request sent, the handler
  called, the code or the status returned, a guarding attribute (`inert`,
  `form=`); not a class, the layout or a text, and not what a mock was told
  to return. Markup that assembles the next request is a decision, not the
  look.
- **An existing test** — an audit removes one that proves nothing, and one
  whose break the live check of the change itself would show, a break of
  the look alone among them. A test of a break that happens silently, or
  somewhere else, stays, even where a new change would not have required it.
- **A test of a code convention** — the module graph, the language of
  messages, the number of queries as the data grows — is a deterministic
  check, like a lint rule: the risk rule neither asks for it nor removes it,
  and it lives as long as the convention does.

Observed on a live project: a test audit that removed everything outside the
first six classes would have dropped about a dozen groups of frontend tests
and several backend ones that guarded silent breaks — an empty choice read
as the whole history, drafts overwritten without their fingerprints, a page
hold that leaked, a key reaching a delete button, a scroll lock in every
dialog — and a rule against checking HTML had pushed its first pass that way.
