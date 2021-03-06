import csv
import itertools
import sys

PROBS = {

    # Unconditional probabilities for having gene
    "gene": {
        2: 0.01,
        1: 0.03,
        0: 0.96
    },

    "trait": {

        # Probability of trait given two copies of gene
        2: {
            True: 0.65,
            False: 0.35
        },

        # Probability of trait given one copy of gene
        1: {
            True: 0.56,
            False: 0.44
        },

        # Probability of trait given no gene
        0: {
            True: 0.01,
            False: 0.99
        }
    },

    # Mutation probability
    "mutation": 0.01
}


def main():

    # Check for proper usage
    if len(sys.argv) != 2:
        sys.exit("Usage: python heredity.py data.csv")
    people = load_data(sys.argv[1])

    # Keep track of gene and trait probabilities for each person
    probabilities = {
        person: {
            "gene": {
                2: 0,
                1: 0,
                0: 0
            },
            "trait": {
                True: 0,
                False: 0
            }
        }
        for person in people
    }

    # Loop over all sets of people who might have the trait
    names = set(people)
    for have_trait in powerset(names):

        # Check if current set of people violates known information
        fails_evidence = any(
            (people[person]["trait"] is not None and
             people[person]["trait"] != (person in have_trait))
            for person in names
        )
        if fails_evidence:
            continue

        # Loop over all sets of people who might have the gene
        for one_gene in powerset(names):
            for two_genes in powerset(names - one_gene):

                # Update probabilities with new joint probability
                p = joint_probability(people, one_gene, two_genes, have_trait)
                update(probabilities, one_gene, two_genes, have_trait, p)

    # Ensure probabilities sum to 1
    normalize(probabilities)

    # Print results
    for person in people:
        print(f"{person}:")
        for field in probabilities[person]:
            print(f"  {field.capitalize()}:")
            for value in probabilities[person][field]:
                p = probabilities[person][field][value]
                print(f"    {value}: {p:.4f}")


def load_data(filename):
    """
    Load gene and trait data from a file into a dictionary.
    File assumed to be a CSV containing fields name, mother, father, trait.
    mother, father must both be blank, or both be valid names in the CSV.
    trait should be 0 or 1 if trait is known, blank otherwise.
    """
    data = dict()
    with open(filename) as f:
        reader = csv.DictReader(f)
        for row in reader:
            name = row["name"]
            data[name] = {
                "name": name,
                "mother": row["mother"] or None,
                "father": row["father"] or None,
                "trait": (True if row["trait"] == "1" else
                          False if row["trait"] == "0" else None)
            }
    return data


def powerset(s):
    """
    Return a list of all possible subsets of set s.
    """
    s = list(s)
    return [
        set(s) for s in itertools.chain.from_iterable(
            itertools.combinations(s, r) for r in range(len(s) + 1)
        )
    ]


def joint_probability(people, one_gene, two_genes, have_trait):
    """
    Compute and return a joint probability.

    The probability returned should be the probability that
        * everyone in set `one_gene` has one copy of the gene, and
        * everyone in set `two_genes` has two copies of the gene, and
        * everyone not in `one_gene` or `two_gene` does not have the gene, and
        * everyone in set `have_trait` has the trait, and
        * everyone not in set` have_trait` does not have the trait.
    """
    probability = 1.0
    for person in people:
        mom = people[person]['mother']
        dad = people[person]['father']
        personTrait = True if person in have_trait else False
        personGene = getGene(person, one_gene, two_genes)

        
        if dad is None and mom is None:
            probability *= PROBS["trait"][personGene][personTrait] * PROBS["gene"][personGene]
        else:
            mom_genes = getGene(mom, one_gene, two_genes)
            dad_genes = getGene(dad, one_gene, two_genes)

            if personGene == 0:
                probability *= inherit(mom_genes, False) * inherit(dad_genes, False)
            elif personGene == 1:
                probability *= (inherit(mom_genes, True) * inherit(dad_genes, False) + inherit(mom_genes, False) * inherit(dad_genes, True))
            elif personGene == 2:
                probability *= inherit(mom_genes, True) * inherit(dad_genes, True)
            probability *= PROBS["trait"][personGene][personTrait]
    return probability



def getGene(person ,one_gene, two_gene ):
    """Return the number of genes the person has

    Args:
        person : 
        one_gene (List): list of people with one copy of gene
        two_gene (List): list of people with two copy of gene

    Returns:
        Int: the number associated with the gene
    """
    return 1 if person in one_gene else 2 if person in two_gene else 0

def inherit(parent_gene, trait):
    """Returns the odds of inheriting a gene

    Args:
        parent_gene (Int): 0, 1, or 2 depending on how many copy of genes the parent has
        trait (Bool): Does the child show the trait

    Returns:
        [type]: [description]
    """
    if parent_gene == 0:
        return  PROBS["mutation"] if trait else 1 - PROBS["mutation"]
    elif parent_gene == 1:
        return  0.5
    elif parent_gene == 2:
        return  1- PROBS["mutation"] if trait else PROBS["mutation"]


def update(probabilities, one_gene, two_genes, have_trait, p):
    """
    Add to `probabilities` a new joint probability `p`.
    Each person should have their "gene" and "trait" distributions updated.
    Which value for each distribution is updated depends on whether
    the person is in `have_gene` and `have_trait`, respectively.
    """

    for person in probabilities:
        personGene = getGene(person, one_gene, two_genes)        
        personTrait = True if person in have_trait else False
        
        probabilities[person]["gene"][personGene] += p
        probabilities[person]["trait"][personTrait] += p

def normalize(probabilities):
    """
    Update `probabilities` such that each probability distribution
    is normalized (i.e., sums to 1, with relative proportions the same).
    """
    for person in probabilities:
        # Summing each genes and traits
        sum_gene = sum(probabilities[person]["gene"].values())
        sum_trait = sum(probabilities[person]["trait"].values())
        
        # Divide each entry by the sum to normalize it
        for trait in probabilities[person]["trait"]:
            probabilities[person]["trait"][trait] = probabilities[person]["trait"][trait] / sum_trait
        
        for gene in probabilities[person]["gene"]:
            probabilities[person]["gene"][gene] = probabilities[person]["gene"][gene] / sum_gene


if __name__ == "__main__":
    main()
