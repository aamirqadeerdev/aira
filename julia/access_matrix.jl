# ── AIRA Julia Access Matrix Engine ──
# Large-scale permission matrix operations.
# Handles thousands of identities x resources efficiently.

module AccessMatrix

export build_access_matrix, detect_conflicts, compute_privilege_score

"""
Build a permission matrix for identities x resources.
Returns a binary matrix: 1 = has access, 0 = no access.
"""
function build_access_matrix(
    n_identities::Int,
    n_resources::Int,
    permissions::Vector{Tuple{Int, Int}}
)::Matrix{Int}

    matrix = zeros(Int, n_identities, n_resources)

    for (identity_idx, resource_idx) in permissions
        if 1 <= identity_idx <= n_identities && 1 <= resource_idx <= n_resources
            matrix[identity_idx, resource_idx] = 1
        end
    end

    return matrix
end

"""
Detect separation of duties conflicts in access matrix.
Returns list of conflicting identity indices.
"""
function detect_conflicts(
    access_matrix::Matrix{Int},
    conflicting_pairs::Vector{Tuple{Int, Int}}
)::Vector{Int}

    n_identities = size(access_matrix, 1)
    conflicts    = Int[]

    for identity in 1:n_identities
        for (res_a, res_b) in conflicting_pairs
            if access_matrix[identity, res_a] == 1 && access_matrix[identity, res_b] == 1
                push!(conflicts, identity)
                break
            end
        end
    end

    return unique(conflicts)
end

"""
Compute privilege score for each identity.
Higher score = more access = higher risk.
"""
function compute_privilege_score(
    access_matrix::Matrix{Int},
    resource_weights::Vector{Float64}
)::Vector{Float64}

    n_identities = size(access_matrix, 1)
    scores       = zeros(Float64, n_identities)
    max_score    = sum(resource_weights)

    for identity in 1:n_identities
        raw_score = sum(access_matrix[identity, :] .* resource_weights)
        scores[identity] = clamp((raw_score / max_score) * 100.0, 0.0, 100.0)
    end

    return scores
end

"""
Find identities with excessive access (outliers).
Returns indices of identities with score above threshold.
"""
function find_excessive_access(
    privilege_scores::Vector{Float64},
    threshold::Float64 = 75.0
)::Vector{Int}

    return findall(s -> s >= threshold, privilege_scores)
end

end # module
