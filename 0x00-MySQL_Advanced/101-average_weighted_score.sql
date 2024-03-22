-- Creates a stored procedure ComputeAverageWeightedScoreForUsers that computes
-- and store the average weighted score for all students
DROP PROCEDURE IF EXISTS ComputeAverageWeightedScoreForUsers;
DELIMITER //
CREATE PROCEDURE ComputeAverageWeightedScoreForUsers ()
BEGIN
    ALTER TABLE users ADD total_weighted_score INT NOT NULL;
    ALTER TABLE users ADD total_weight INT NOT NULL;

    -- Calculate total weighted score for each user
    UPDATE users
        SET total_weighted_score = (
            SELECT SUM(corrections.score * projects.weight)
            FROM corrections
            INNER JOIN projects ON corrections.project_id = projects.id
            WHERE corrections.user_id = users.id
        );

    -- Calculate total weight for each user
    UPDATE users
        SET total_weight = (
            SELECT SUM(projects.weight)
            FROM corrections
            INNER JOIN projects ON corrections.project_id = projects.id
            WHERE corrections.user_id = users.id
        );

    -- Update average_score for each user based on total weighted score and total weight
    UPDATE users
        SET users.average_score = IF(users.total_weight = 0, 0, users.total_weighted_score / users.total_weight);

    -- Drop temporary columns
    ALTER TABLE users DROP COLUMN total_weighted_score;
    ALTER TABLE users DROP COLUMN total_weight;
END;
//
DELIMITER ;
